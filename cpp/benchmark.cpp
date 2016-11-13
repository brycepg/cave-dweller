#include <benchmark/benchmark.h>

#include "gen_map.h"

static void BM_gen_map(benchmark::State& state) {
    int* map;
    while (state.KeepRunning()) {
        benchmark::DoNotOptimize(map = gen_map(0,0,0));
    }
}
static void BM_gen_map2(benchmark::State& state) {
    int* map;
    while (state.KeepRunning()) {
        benchmark::DoNotOptimize(map = gen_map2(0,0,0));
    }
}
static void BM_gen_map3(benchmark::State& state) {
    int** map;
    while (state.KeepRunning()) {
        benchmark::DoNotOptimize(map = gen_map3(0,0,0));
    }
}
BENCHMARK(BM_gen_map);
BENCHMARK(BM_gen_map2);
BENCHMARK(BM_gen_map3);
BENCHMARK_MAIN();
