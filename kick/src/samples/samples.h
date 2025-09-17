#ifndef SAMPLES_H
#define SAMPLES_H

// Include all individual sample headers
#include "sample01.h"
#include "sample02.h"
#include "sample03.h"
#include "sample04.h"
#include "sample05.h"
#include "sample06.h"
#include "sample07.h"
#include "sample08.h"

// Array of sample pointers for easy access
const uint8_t* const samples[] = {sample01, sample02, sample03, sample04,
                                  sample05, sample06, sample07, sample08};

// Array of sample lengths
const uint32_t sample_lengths[] = {SAMPLE01_LEN, SAMPLE02_LEN, SAMPLE03_LEN,
                                   SAMPLE04_LEN, SAMPLE05_LEN, SAMPLE06_LEN,
                                   SAMPLE07_LEN, SAMPLE08_LEN};

#define NUM_SAMPLES (sizeof(samples) / sizeof(samples[0]))

#endif  // SAMPLES_H
