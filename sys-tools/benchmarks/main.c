#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pixel.h"
#include <unistd.h>
int wait = 2000000;

long itr = 5000000000;
int ioitr = 500;

void iobench() {
    if (init_framebuffer() != 0) {
        fprintf(stderr, "error init frames (main)\n");
        return 1;
    } else {
        printf("framebuffer init success: clearing screen to test\n");
    }
    usleep(wait * 2);
    for (int i = 0; i < ioitr; i++) {
        draw_rect(0, 0, screen_res_x, screen_res_y, 0x00000);
    }
    
    close_framebuffer();
}

int get_thread() {
    long threads = sysconf(_SC_NPROCESSORS_ONLN);
    return (threads > 0) ? (int)threads : 1;
}

void simpbench(void *arg) {
   	long start = ((long *)arg)[0];
   	long end = ((long *)arg)[1];
   	volatile long sum = 0;
    for (long i = start; i < end; i++) {
        sum = (sum + i) * 3 - i / 2;
    }
    return NULL;
}

void thrbench(int threads) {
    pthread_t tids[threads];
	long ranges[threads][2];
	long chunk = itr / threads;
    for (int i = 0; i < threads; i++) {
    	ranges[i][0] = i * chunk;
    	ranges[i][1] = (i == threads - 1) ? itr : (i + 1) * chunk;
        pthread_create(&tids[i], NULL, simpbench, ranges[i]);
    }
    
    for (int i = 0; i < threads; i++) {
        pthread_join(tids[i], NULL);
    }
}


int main() {
    struct timespec start, end;
    int threads = get_thread();
    printf("cpu math iterations: %ld\nio iterations %d\ncpu threads found %d\n", itr, ioitr, threads);
	printf("warming cpu\n");
	long warmup_range[2] = {0, 400000000};
	simpbench((void *)warmup_range);
	printf("starting signle core test\n");
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start);
	long test_range[2] = {0, itr};
    simpbench((void *)test_range);
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end);
    double time_1 = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("time taken for single thread test: %.3f\n", time_1);
    printf("warming up all cores\n");
    thrbench(threads, (itr / 10));
    printf("starting all cores test\n");
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &start); 
    thrbench(threads, 0);
    clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &end);
    double time_2 = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("time taken for multi-thread test: %.3f\n", time_2);
    usleep(wait);

    printf("score = %.4f\n", ((time_1 + time_2) / 2) * 100);

/*    clock_gettime(CLOCK_MONOTONIC, &start);
    printf("starting IO test\n");
    iobench();
    clock_gettime(CLOCK_MONOTONIC, &end);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("time taken for IO test: %.3f\n", time_taken);
*/
    
    return 1;
}
