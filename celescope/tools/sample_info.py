#!/bin/env python
# coding=utf8

import os
import pandas as pd
import sys
import logging
from celescope.tools.__version__ import __VERSION__
from celescope.tools.report import reporter

logger1 = logging.getLogger(__name__)
ASSAY_DICT = {"rna": "Single Cell RNA-Seq",
            "rna_virus": "Single Cell RNA-Seq Virus",
            'capture_virus': "Single cell Capture Virus"
            }


def sample_info(args):
    if not os.path.exists(args.outdir):
        os.system('mkdir -p %s' % args.outdir)
    sample = args.sample
    ASSAY = ASSAY_DICT[args.assay]
    version = __VERSION__
    outdir = args.outdir
    chemistry = args.chemistry
    if not chemistry:
        chemistry = "Customized"
    #transcriptome = args.genomeDir.split("/")[-1]

    if not os.path.exists(outdir):
        os.system('mkdir -p %s' % outdir)

    stat = pd.DataFrame({"item": ["Sample ID", "Assay", "Chemistry", "Software Version"],
        "count": [sample, ASSAY, chemistry, version]}, columns=["item", "count"])
    stat_file = outdir + "/stat.txt"
    stat.to_csv(stat_file, sep=":", header=None, index=False)

    t = reporter(name='sample', assay=args.assay, sample=args.sample, stat_file=stat_file, outdir=outdir + '/..')
    t.get_report()
    logger1.info("Generating sample info done.")


def get_opts_sample(parser, sub_program):
    if sub_program:
        parser.add_argument('--outdir', help='output dir', required=True)
        parser.add_argument('--sample', help='sample name', required=True)
        parser.add_argument('--genomeDir', help='genomeDir', required=True)
        parser.add_argument('--assay', help='assay', required=True)
    parser.add_argument('--chemistry', help='chemistry')