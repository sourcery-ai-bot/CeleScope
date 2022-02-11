## Features
- Filter background virus UMIs base on a UMI threshold.
There are three methods to determine the UMI threshold:
    - 'auto' : Using a method similar to cell calling method.
    - 'otsu' : UMI counts are first log 2 transformed and then the threshold is determined by [Otsu's method](https://en.wikipedia.org/wiki/Otsu%27s_method)
    - 'hard' : Using User provided UMI threshold.

## Output
- {sample}_filtered_UMI_tsne.csv : Filtered virus UMI counts of each cell barcode.


## Arguments
`--not_correct_UMI` Perform UMI correction.

`--read_threshold_method` method to find read threshold. UMIs with `support reads` < `read threshold` are filtered.

`--read_hard_threshold` int, use together with `--read_threshold_method hard`.

`--umi_threshold_method` method to find UMI threshold. Cell barcode with `UMI` < `UMI threshold` are considered negative.

`--umi_hard_threshold` int, use together with `--umi_threshold_method hard`.

`--match_dir` Match celescope scRNA-Seq directory.

`--raw_read_count_file` None

`--outdir` Output diretory.

`--sample` Sample name.

`--thread` Thread to use.

`--debug` If this argument is used, celescope may output addtional file for debugging.
