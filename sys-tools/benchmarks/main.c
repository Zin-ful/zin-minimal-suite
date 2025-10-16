#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "pixel.h"
#include <unistd.h>
int wait = 2000000;

long itr = 500000000;
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

void simpbench() {
    volatile long sum = 0;
    for (long i = 0; i < itr; i++) {
        sum = (sum + i) * 3 - i / 2;
    }
}

void thrbench(threads) {
    pthread_t tids[threads];
    for (int i = 0; i < threads; i++) {
        pthread_create(&tids[i], NULL, simpbench, (void*)(size_t)i);
    }
    
    for (int i = 0; i < threads; i++) {
        pthread_join(tids[i], NULL);
    }
}


int main() {
    struct timespec start, end;
    int threads = get_thread();
    printf("cpu math iterations: %ld\nio iterations %d\ncpu threads found %d\n", itr, ioitr, threads);
    clock_gettime(CLOCK_MONOTONIC, &start);
    simpbench();
    clock_gettime(CLOCK_MONOTONIC, &end);
    double time_1 = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("time taken for single thread test: %.3f\n", time_1);

    clock_gettime(CLOCK_MONOTONIC, &start); 
    thrbench(threads);
    clock_gettime(CLOCK_MONOTONIC, &end);
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
