#define NONIUS_RUNNER
#include "nonius/nonius.h++"

#include "gen_map.h"

NONIUS_BENCHMARK("gen_map", []{
    int* map;
    map = gen_map(0,0,0);
    return gen_map;
})
//static void BM_gen_map2(benchmark::State& state) {
//    int* map;
//    while (state.KeepRunning()) {
//        benchmark::DoNotOptimize(map = gen_map2(0,0,0));
//    }
//}
//static void BM_gen_map3(benchmark::State& state) {
//    int** map;
//    while (state.KeepRunning()) {
//        benchmark::DoNotOptimize(map = gen_map3(0,0,0));
//    }
//}
