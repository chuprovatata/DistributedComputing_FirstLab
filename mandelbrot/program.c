#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include "timer.h"
#include <time.h>

#define MAX_ITER 1000
#define BATCH_SIZE 100

#define MIN_X -2.0
#define MAX_X 1.0

#define MIN_Y -1.0
#define MAX_Y 1.0

int nthreads;
int npoints;

int stop_flag = 0;
int global_points_count = 0;

FILE* results_file;

pthread_mutex_t mutex;

typedef struct {
    double x;
    double y;
} Point;

int is_in_mandelbrot(double c_real, double c_imag) {
    double z_real = 0.0;
    double z_imag = 0.0;

    for (int i = 0; i < MAX_ITER; i++) {
        double z_real_sq = z_real * z_real;
        double z_imag_sq = z_imag * z_imag;

        double new_z_real = z_real_sq - z_imag_sq + c_real;
        double new_z_imag = 2.0 * z_real * z_imag + c_imag;

        z_real = new_z_real;
        z_imag = new_z_imag;

        if (z_real * z_real + z_imag * z_imag >= 4.0) {
            return 0;
        }
    }
    return 1;
}

void* routine(void* rank) {
    long my_rank = (long) rank;

    unsigned int seed = (unsigned int)(time(NULL) ^ my_rank);

    Point local_points[BATCH_SIZE];

    while (1) {
        pthread_mutex_lock(&mutex);
        int should_stop = stop_flag;
        pthread_mutex_unlock(&mutex);

        if (should_stop) {
            break;
        }

        int local_count = 0;

        for (int i = 0; i < BATCH_SIZE; i++) {
            double x = (double)rand_r(&seed) / RAND_MAX * (MAX_X - MIN_X) + MIN_X;
            double y = (double)rand_r(&seed) / RAND_MAX * (MAX_Y - MIN_Y) + MIN_Y;

            if (is_in_mandelbrot(x, y)) {
                local_points[local_count].x = x;
                local_points[local_count].y = y;
                local_count++;
            }
        }

        pthread_mutex_lock(&mutex);

        for (int i = 0; i < local_count; i++) {
            if (global_points_count >= npoints) {
                stop_flag = 1;
                break;
            }

            fprintf(results_file,"%.6lf,%.6lf\n",local_points[i].x,local_points[i].y);
            global_points_count++;

            if (global_points_count >= npoints) {
                stop_flag = 1;
                break;
            }
        }
        pthread_mutex_unlock(&mutex);
    }

    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "How to launch: %s <threads_count> <points_count>\n", argv[0]);
        return 1;
    }

    nthreads = atoi(argv[1]);
    npoints = atoi(argv[2]);

    if (nthreads <= 0 || npoints <= 0) {
        fprintf(stderr, "Error: arguments must be positive\n");
        return 1;
    }

    pthread_t* thread_handles = malloc(sizeof(pthread_t) * nthreads);

    if (thread_handles == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    char filename[100];
    sprintf(filename, "csv_results/set_%d_%d.csv", nthreads, npoints);
    results_file = fopen(filename, "w");

    if (results_file == NULL) {
        perror("Error opening results file");
        free(thread_handles);
        return 1;
    }

    fprintf(results_file, "x,y\n");
    pthread_mutex_init(&mutex, NULL);

    double start, end;
    GET_TIME(start);
    for (long i = 0; i < nthreads; i++) {
        pthread_create(&thread_handles[i], NULL, routine, (void*) i);
    }

    for (int i = 0; i < nthreads; i++) {
        pthread_join(thread_handles[i], NULL);
    }
    GET_TIME(end);

    double elapsed_time = end - start;
    fprintf(stdout, "%d,%d,%lf\n", nthreads, npoints, elapsed_time);

    fclose(results_file);
    pthread_mutex_destroy(&mutex);
    free(thread_handles);
    return 0;
}