/**********************************************************************

  resamplesubs.c

  Real-time library interface by Dominic Mazzoni

  Based on resample-1.7:
    http://www-ccrma.stanford.edu/~jos/resample/

  License: LGPL - see the file LICENSE.txt for more information

**********************************************************************/

/* Definitions */
#include "resample_defs.h"

/*
 * FilterUp() - Applies a filter to a given sample when up-converting.
 * FilterUD() - Applies a filter to a given sample when up- or down-
 */

double lrsFilterUp(double Imp[], double ImpD[], UWORD Nwing, BOOL Interp,
                  double *Xp, double Ph, int Inc);

double lrsFilterUD(double Imp[], double ImpD[], UWORD Nwing, BOOL Interp,
                  double *Xp, double Ph, int Inc, double dhb);

void lrsLpFilter(double c[], int N, double frq, double Beta, int Num);
