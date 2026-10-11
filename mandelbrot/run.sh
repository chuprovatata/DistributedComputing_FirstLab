#!/bin/bash

set -e

clang -O2 -pthread program.c -o program

mkdir -p csv_results

echo "threads,points,average_time" > performance_results.csv
echo "threads,points,run,time" > performance_details.csv

# Информация об аппаратной архитектуре
{
    echo "Hardware information"
    echo "===================="
    echo "Processor: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || sysctl -n hw.model)"
    echo "Architecture: $(uname -m)"
    echo "Logical CPUs: $(sysctl -n hw.logicalcpu)"
    echo "Physical CPUs: $(sysctl -n hw.physicalcpu)"
    echo "Memory (bytes): $(sysctl -n hw.memsize)"
    echo "macOS: $(sw_vers -productVersion)"
    echo "Compiler: $(clang --version | head -n 1)"
    echo "Optimization: -O2"
    echo "Runs per configuration: 10"
} > hardware_info.txt

for points in 10000 100000 1000000 10000000
do
    for threads in 1 2 4 8
    do
        total_time=0

        for run in {1..10}
        do
            echo "Running: threads=$threads, points=$points, run=$run"

            result=$(./program "$threads" "$points")

            time_value=${result##*,}

            echo "$threads,$points,$run,$time_value" >> performance_details.csv

            total_time=$(awk -v total="$total_time" -v time="$time_value" \
                'BEGIN {printf "%.10f", total + time}')
        done

        average_time=$(awk -v total="$total_time" \
            'BEGIN {printf "%.6f", total / 10}')

        echo "$threads,$points,$average_time" >> performance_results.csv

        echo "Average time: $average_time seconds"
        echo "----------------------------------------"
    done
done

echo "All experiments completed!"
