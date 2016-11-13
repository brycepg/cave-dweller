// Copyright (c) 2008, Casey Duncan (casey dot duncan at gmail dot com)
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include "noise.h"

// Dropped PI in c99
#define M_1_PI 0.31830988618379067154

#define dot3(v1, v2) ((v1)[0]*(v2)[0] + (v1)[1]*(v2)[1] + (v1)[2]*(v2)[2])

#define ASSIGN(a, v0, v1, v2) (a)[0] = v0; (a)[1] = v1; (a)[2] = v2;

#define F3 (1.0f / 3.0f)
#define G3 (1.0f / 6.0f)

float 
noise3(float x, float y, float z) 
{
	int c, o1[3], o2[3], g[4], I, J, K;
	float f[4], noise[4] = {0.0f, 0.0f, 0.0f, 0.0f};
	float s = (x + y + z) * F3;
	float i = floorf(x + s);
	float j = floorf(y + s);
	float k = floorf(z + s);
	float t = (i + j + k) * G3;

	float pos[4][3];

	pos[0][0] = x - (i - t);
	pos[0][1] = y - (j - t);
	pos[0][2] = z - (k - t);

	if (pos[0][0] >= pos[0][1]) {
		if (pos[0][1] >= pos[0][2]) {
			ASSIGN(o1, 1, 0, 0);
			ASSIGN(o2, 1, 1, 0);
		} else if (pos[0][0] >= pos[0][2]) {
			ASSIGN(o1, 1, 0, 0);
			ASSIGN(o2, 1, 0, 1);
		} else {
			ASSIGN(o1, 0, 0, 1);
			ASSIGN(o2, 1, 0, 1);
		}
	} else {
		if (pos[0][1] < pos[0][2]) {
			ASSIGN(o1, 0, 0, 1);
			ASSIGN(o2, 0, 1, 1);
		} else if (pos[0][0] < pos[0][2]) {
			ASSIGN(o1, 0, 1, 0);
			ASSIGN(o2, 0, 1, 1);
		} else {
			ASSIGN(o1, 0, 1, 0);
			ASSIGN(o2, 1, 1, 0);
		}
	}
	
	for (c = 0; c <= 2; c++) {
		pos[3][c] = pos[0][c] - 1.0f + 3.0f * G3;
		pos[2][c] = pos[0][c] - o2[c] + 2.0f * G3;
		pos[1][c] = pos[0][c] - o1[c] + G3;
	}

	I = (int) i & 255; 
	J = (int) j & 255; 
	K = (int) k & 255;
	g[0] = PERM[I + PERM[J + PERM[K]]] % 12;
	g[1] = PERM[I + o1[0] + PERM[J + o1[1] + PERM[o1[2] + K]]] % 12;
	g[2] = PERM[I + o2[0] + PERM[J + o2[1] + PERM[o2[2] + K]]] % 12;
	g[3] = PERM[I + 1 + PERM[J + 1 + PERM[K + 1]]] % 12; 

	for (c = 0; c <= 3; c++) {
		f[c] = 0.6f - pos[c][0]*pos[c][0] - pos[c][1]*pos[c][1] - pos[c][2]*pos[c][2];
	}
	
	for (c = 0; c <= 3; c++) {
		if (f[c] > 0) {
			noise[c] = f[c]*f[c]*f[c]*f[c] * dot3(pos[c], GRAD3[g[c]]);
		}
	}
	
	return (noise[0] + noise[1] + noise[2] + noise[3]) * 32.0f;
}
float fbm_noise3(float x, float y, float z, int octaves, float persistence, float lacunarity) {
    float freq = 1.0f;
    float amp = 1.0f;
    float max = 1.0f;
    float total = noise3(x, y, z);
    int i;

    for (i = 1; i < octaves; ++i) {
        freq *= lacunarity;
        amp *= persistence;
        max += amp;
        total += noise3(x * freq, y * freq, z * freq) * amp;
    }
    return total / max;
}
