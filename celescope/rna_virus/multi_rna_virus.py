from celescope.rna_virus.__init__ import __STEPS__, __ASSAY__
from celescope.tools.Multi import Multi


class Multi_rna_virus(Multi):


    def STAR_virus(self, sample):
        step = 'STAR_virus'
        input_read = f'{self.outdir_dic[sample]["cutadapt"]}/{sample}_clean_2.fq.gz'
        cmd_line = self.get_cmd_line(step, sample)
        cmd = (
            f'{cmd_line} '
            f'--input_read {input_read} '

        )
        self.process_cmd(cmd, step, sample, m=self.args.starMem, x=self.args.thread)

    def count_virus(self, sample):
        step = 'count_virus'
        barcode_file = f'{self.outdir_dic[sample]["count"]}/{sample}_matrix_10X/barcodes.tsv'
        virus_bam = f'{self.outdir_dic[sample]["STAR_virus"]}/{sample}_virus_Aligned.sortedByCoord.out.bam'
        cmd_line = self.get_cmd_line(step, sample)
        cmd = (
            f'{cmd_line} '
            f'--virus_bam {virus_bam} '
            f'--barcode_file {barcode_file} '
        )
        self.process_cmd(cmd, step, sample, m=5, x=1)

    def analysis_rna_virus(self, sample):        
        step = 'analysis_rna_virus'
        virus_file = f'{self.outdir_dic[sample]["count_virus"]}/{sample}_virus_UMI_count.tsv'
        matrix_file = f'{self.outdir_dic[sample]["count"]}/{sample}_matrix.tsv.gz'
        cmd_line = self.get_cmd_line(step, sample)
        cmd = (
            f'{cmd_line} '
            f'--virus_file {virus_file} '
            f'--matrix_file {matrix_file} '

        )
        self.process_cmd(cmd, step, sample, m=15, x=1)


def main():
    multi = Multi_rna_virus(__ASSAY__)
    multi.run()


if __name__ == '__main__':
    main()
