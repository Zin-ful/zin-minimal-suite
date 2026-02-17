/*


 Tests:
   1. Integer arithmetic  — single core
   2. Integer arithmetic  — all cores
   3. Floating point throughput
   4. Memory bandwidth    (sequential STREAM triad)
   5. Cache hierarchy     (L1 → L2 → L3 → RAM latency by working-set size)
   6. Memory latency      (pointer-chase, defeats prefetcher)
   7. Branch prediction   (predictable vs unpredictable)
   8. Boost / throttle    (sustained single-core ops/s over time)
   add -lm to gcc
*/

#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <pthread.h>

#include <time.h>
#include <unistd.h>
#include <math.h>

/* ------tuning------ */

static long  INT_ITR        = 5000000000L; /* integer bench iterations      */
static long  FP_ITR         = 2000000000L; /* FP bench iterations           */
static long  BRANCH_ITR     = 500000000L;  /* branch bench iterations       */
static long  STREAM_BYTES   = 512L * 1024 * 1024; /* 512 MB stream buffer   */
static int   CHASE_NODES    = 64 * 1024 * 1024;   /* ~256 MB pointer chase  */
static int   BOOST_STEPS    = 10;          /* number of boost samples        */
static long  BOOST_ITR      = 500000000L;  /* iterations per boost sample   */
static int   WAIT_US        = 2000000;

#define MAX_THREADS 512

/* cache sizes to probe (bytes)*/
static const size_t CACHE_SIZES[] = {
    8   * 1024,          /*   8 KB  — fits in L1  */
    128 * 1024,          /* 128 KB  — fits in L2  */
    4   * 1024 * 1024,   /*   4 MB  — fits in L3  */
    128 * 1024 * 1024,   /* 128 MB  — RAM          */
};
#define N_CACHE_SIZES ((int)(sizeof(CACHE_SIZES)/sizeof(CACHE_SIZES[0])))

/*---------helpers---------*/

static int get_thread_count(void) {
    long n = sysconf(_SC_NPROCESSORS_ONLN);
    return (n > 0) ? (int)n : 1;
}

static double elapsed(struct timespec a, struct timespec b) {
    return (b.tv_sec - a.tv_sec) + (b.tv_nsec - a.tv_nsec) / 1e9;
}

static void ts_mono(struct timespec *t)  { clock_gettime(CLOCK_MONOTONIC,         t); }
static void ts_cpu (struct timespec *t)  { clock_gettime(CLOCK_PROCESS_CPUTIME_ID, t); }

/*-------integer arithmetic---------------*/

static void *int_worker(void *arg) {
    long start = ((long *)arg)[0];
    long end   = ((long *)arg)[1];
    volatile long sum = 0;
    for (long i = start; i < end; i++) {
        sum = (sum + i) * 3 - i / 2;
    }
    (void)sum;
    return NULL;
}

static void run_threaded(int threads, long total_itr, void *(*worker)(void *)) {
    pthread_t tids[MAX_THREADS];
    long      ranges[MAX_THREADS][2];
    if (threads > MAX_THREADS) threads = MAX_THREADS;
    long chunk = total_itr / threads;
    for (int i = 0; i < threads; i++) {
        ranges[i][0] = (long)i * chunk;
        ranges[i][1] = (i == threads - 1) ? total_itr : (long)(i + 1) * chunk;
        pthread_create(&tids[i], NULL, worker, ranges[i]);
    }
    for (int i = 0; i < threads; i++) pthread_join(tids[i], NULL);
}

/*-------floating-point throughput---------*/

static void *fp_worker(void *arg) {
    long start = ((long *)arg)[0];
    long end   = ((long *)arg)[1];
    volatile double acc = 1.0;
    for (long i = start; i < end; i++) {
        /* mix of multiply, sqrt, add — resists trivial vectorisation */
        acc = acc * 1.0000003 + sqrt((double)(i & 0xFFFFF) + 1.0) * 0.000001;
    }
    (void)acc;
    return NULL;
}

/*--------memory bandwidth-------*/

static double membw_bench(void) {
    long n = STREAM_BYTES / (long)sizeof(float);
    float *A = malloc((size_t)n * sizeof(float));
    float *B = malloc((size_t)n * sizeof(float));
    float *C = malloc((size_t)n * sizeof(float));
    if (!A || !B || !C) {
        free(A); free(B); free(C);
        fprintf(stderr, "membw: allocation failed (need ~%.0f MB)\n",
                n * 3.0 * sizeof(float) / (1024*1024));
        return -1.0;
    }
    for (long i = 0; i < n; i++) { A[i] = (float)i * 0.5f; B[i] = 1.0f; }

    float scalar = 2.5f;
    struct timespec t0, t1;
    ts_mono(&t0);
    for (long i = 0; i < n; i++) C[i] = A[i] + scalar * B[i];
    ts_mono(&t1);

    volatile float sink = C[n / 2]; (void)sink;

    double secs = elapsed(t0, t1);
    double gb   = (3.0 * (double)n * sizeof(float)) / (1024.0 * 1024 * 1024);
    free(A); free(B); free(C);
    return gb / secs;  /* GB/s */
}

/*------cache hierarchy-----------*/

static void cache_bench(void) {
    printf("\n5: cache hierarchy\n");
    printf("    %-14s  %10s  %10s\n", "working set", "ns/elem", "MB/s");

    for (int s = 0; s < N_CACHE_SIZES; s++) {
        size_t sz   = CACHE_SIZES[s];
        long   n    = (long)(sz / sizeof(uint32_t));
        long   reps = (long)(256L * 1024 * 1024 / (long)sz);
        if (reps < 4) reps = 4;

        uint32_t *buf = malloc(sz);
        if (!buf) { printf("    alloc failed for %zu KB\n", sz/1024); continue; }
        for (long i = 0; i < n; i++) buf[i] = (uint32_t)i;

        volatile uint64_t acc = 0;
        struct timespec t0, t1;
        ts_mono(&t0);
        for (long r = 0; r < reps; r++)
            for (long i = 0; i < n; i++) acc += buf[i];
        ts_mono(&t1);
        (void)acc;

        double secs       = elapsed(t0, t1);
        double total_elem = (double)reps * (double)n;
        double ns_per     = secs * 1e9 / total_elem;
        double mbs        = ((double)reps * (double)sz) / (1024.0*1024) / secs;

        const char *label =
            sz <   64*1024          ? "L1" :
            sz < 1024*1024          ? "L2" :
            sz < 32*1024*1024UL     ? "L3" : "RAM";

        if (sz >= 1024*1024)
            printf("    %4zu MB  (%3s)    %10.2f  %10.0f\n",
                   sz/(1024*1024), label, ns_per, mbs);
        else
            printf("    %4zu KB  (%3s)    %10.2f  %10.0f\n",
                   sz/1024,        label, ns_per, mbs);

        free(buf);
    }
}

/*-----memory latency chase pointers---*/

static void shuffle_ints(int *arr, int n) {
    for (int i = n - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
    }
}

static double chase_bench(void) {
    int  n     = CHASE_NODES;
    int *next  = malloc((size_t)n * sizeof(int));
    int *order = malloc((size_t)n * sizeof(int));
    if (!next || !order) {
        free(next); free(order);
        fprintf(stderr, "chase: alloc failed\n");
        return -1.0;
    }
    for (int i = 0; i < n; i++) order[i] = i;
    srand(42);
    shuffle_ints(order, n);
    for (int i = 0; i < n - 1; i++) next[order[i]] = order[i + 1];
    next[order[n - 1]] = order[0];
    free(order);

    long steps = (long)n * 4;
    struct timespec t0, t1;
    volatile int cur = 0;
    ts_mono(&t0);
    for (long i = 0; i < steps; i++) cur = next[cur];
    ts_mono(&t1);
    (void)cur;

    double ns = elapsed(t0, t1) * 1e9 / (double)steps;
    free(next);
    return ns;
}

/*------branch prediction--------*/

static double branch_bench(int predictable) {
    long n = BRANCH_ITR;
    uint8_t *bits = NULL;

    if (!predictable) {
        bits = malloc((size_t)n);
        if (!bits) { fprintf(stderr, "branch: alloc failed\n"); return -1.0; }
        srand(1234);
        for (long i = 0; i < n; i++) bits[i] = (uint8_t)(rand() & 1);
    }

    volatile long acc = 0;
    struct timespec t0, t1;
    ts_mono(&t0);
    if (predictable) {
        for (long i = 0; i < n; i++) { if (i & 1) acc += i; else acc -= i; }
    } else {
        for (long i = 0; i < n; i++) { if (bits[i]) acc += i; else acc -= i; }
    }
    ts_mono(&t1);
    (void)acc;
    free(bits);
    return elapsed(t0, t1);
}

/*------boost / throttle detection-----*/

static void boost_bench(void) {
    printf("\n8: boost / throttle detection  (%d samples × %ldM itr)\n",
           BOOST_STEPS, BOOST_ITR / 1000000L);
    printf("    %6s  %12s  %s\n", "sample", "Mops/s", "bar");

    long range[2] = {0, BOOST_ITR};
    double first_ops = 0.0;

    for (int s = 0; s < BOOST_STEPS; s++) {
        struct timespec t0, t1;
        ts_cpu(&t0);
        int_worker((void *)range);
        ts_cpu(&t1);
        double secs = elapsed(t0, t1);
        double mops = (BOOST_ITR / 1e6) / secs;
        if (s == 0) first_ops = mops;

        int bar_len = (int)(40.0 * mops / first_ops);
        if (bar_len > 40) bar_len = 40;
        if (bar_len < 1)  bar_len = 1;
        char bar[41];
        memset(bar, '|', (size_t)bar_len);
        bar[bar_len] = '\0';

        printf("    %6d  %12.1f  %s\n", s + 1, mops, bar);
    }
}

/*------main------*/

int main(void) {
    struct timespec t0, t1;
    int threads = get_thread_count();

    printf("========================================\n");
    printf("  CPU & Memory Benchmark\n");
    printf("========================================\n");
    printf("threads detected : %d\n",   threads);
    printf("int iterations   : %ldM\n", INT_ITR    / 1000000L);
    printf("fp  iterations   : %ldM\n", FP_ITR     / 1000000L);
    printf("stream buffer    : %ld MB\n", STREAM_BYTES / (1024*1024));
    printf("chase nodes      : %d M\n", CHASE_NODES / 1000000);
    printf("\n");

    double scores[8];
    memset(scores, 0, sizeof(scores));

    /*--------integer single-core----------*/
    printf("1: integer single-core\n");
    {
        printf("    warming up...\n");
        long warmup[2] = {0, 400000000L};
        int_worker((void *)warmup);

        long range[2] = {0, INT_ITR};
        ts_cpu(&t0);
        int_worker((void *)range);
        ts_cpu(&t1);
        double secs = elapsed(t0, t1);
        printf("    time  : %.3f s\n",       secs);
        printf("    ops/s : %.1f Mops/s\n",  (INT_ITR / 1e6) / secs);
        scores[0] = secs;
    }

    /*----integer multi-core------*/
    printf("\n2: integer multi-core (%d threads)\n", threads);
    {
        printf("    warming up...\n");
        run_threaded(threads, INT_ITR / 10, int_worker);

        ts_mono(&t0);
        run_threaded(threads, INT_ITR, int_worker);
        ts_mono(&t1);
        double secs    = elapsed(t0, t1);
        double speedup = (scores[0] > 0.0) ? scores[0] / secs : 0.0;
        printf("    time    : %.3f s\n",       secs);
        printf("    ops/s   : %.1f Mops/s\n",  (INT_ITR / 1e6) / secs);
        printf("    speedup : %.2fx  (efficiency %.0f%%)\n",
               speedup, speedup / threads * 100.0);
        scores[1] = secs;
    }

    /*--------floating-point throughput-------*/
    printf("\n3: floating-point throughput (%d threads)\n", threads);
    {
        printf("    warming up...\n");
        run_threaded(threads, FP_ITR / 10, fp_worker);

        ts_mono(&t0);
        run_threaded(threads, FP_ITR, fp_worker);
        ts_mono(&t1);
        double secs = elapsed(t0, t1);
        printf("    time  : %.3f s\n",       secs);
        printf("    ops/s : %.1f Mops/s\n",  (FP_ITR / 1e6) / secs);
        scores[2] = secs;
    }

    /*------memory bandwidth-------*/
    printf("\n4: memory bandwidth (STREAM triad, %ld MB buffer)\n",
           STREAM_BYTES / (1024*1024));
    {
        double gbps = membw_bench();
        if (gbps > 0.0) {
            printf("    bandwidth : %.2f GB/s\n", gbps);
            scores[3] = 1.0 / gbps;
        } else {
            printf("    skipped (allocation failed)\n");
        }
    }

    /*-----cache hierarchy------*/
    cache_bench();

    /*----memory latency----------*/
    printf("\n6: memory latency (pointer chase, ~%d MB)\n",
           (int)((size_t)CHASE_NODES * sizeof(int) / (1024*1024)));
    {
        double ns = chase_bench();
        if (ns > 0.0) {
            printf("    avg latency : %.1f ns per access\n", ns);
            scores[5] = ns;
        } else {
            printf("    skipped (allocation failed)\n");
        }
    }

    /*----Branch prediction-------*/
    printf("\n7: branch prediction (%ldM itr)\n", BRANCH_ITR / 1000000L);
    {
        printf("    running predictable...\n");
        double t_pred = branch_bench(1);
        printf("    predictable   : %.3f s\n", t_pred);

        printf("    running unpredictable...\n");
        double t_rand = branch_bench(0);
        printf("    unpredictable : %.3f s\n", t_rand);

        if (t_pred > 0.0)
            printf("    mispred penalty : +%.1f%%\n",
                   (t_rand - t_pred) / t_pred * 100.0);
        scores[6] = t_rand;
    }

    /*--------boost / throttle---------*/
    boost_bench();

    /*-------composite score-----*/
    /*
     mean of normalised times × 1000.
     single-core time, multi-core time, FP time,
     chase latency (converted to seconds), unpredictable branch time.
     lower = faster.
     */
    double contrib[] = {
        scores[0],          /* int single (s)      */
        scores[1],          /* int multi  (s)       */
        scores[2],          /* fp         (s)       */
        scores[5] / 1e9,    /* chase latency → s    */
        scores[6],          /* branch unpred (s)    */
    };
    int    nc      = (int)(sizeof(contrib)/sizeof(contrib[0]));
    double logsum  = 0.0;
    int    valid   = 0;
    for (int i = 0; i < nc; i++) {
        if (contrib[i] > 0.0) { logsum += log(contrib[i]); valid++; }
    }
    double composite = (valid > 0) ? exp(logsum / valid) * 1000.0 : 0.0;

    printf("\n========================================\n");
    printf("  COMPOSITE SCORE  (lower = faster)\n");
    printf("  %.4f\n", composite);
    printf("========================================\n");

    { struct timespec w = { WAIT_US / 1000000, (long)(WAIT_US % 1000000) * 1000L }; nanosleep(&w, NULL); }

    return 0;
}
