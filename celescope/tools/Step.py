import os
import numbers
import json
import io
import pandas as pd
from collections import abc
from collections import namedtuple
from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader

from celescope.tools.utils import add_log


def s_common(parser):
    """subparser common arguments
    """
    parser.add_argument('--outdir', help='output dir', required=True)
    parser.add_argument('--assay', help='assay', required=True)
    parser.add_argument('--sample', help='sample name', required=True)
    parser.add_argument('--thread', default=4)
    parser.add_argument('--debug', help='debug', action='store_true')
    return parser


class Step:
    '''
    Step class
    '''
    def __init__(self, args, step_name):
        self.step_name = step_name
        self.args = args
        self.outdir = args.outdir
        # check dir
        if not os.path.exists(self.outdir):
            os.system('mkdir -p %s' % self.outdir)
        self.sample = args.sample
        self.assay = args.assay
        self.thread = args.thread
        self.debug = args.debug
        self.stat_file = f'{self.outdir}/stat.txt'
        self.metric_list = []
        self.Metric = namedtuple("Metric", "name value total fraction")
        self.path_dict = {
            "metric": f'{self.outdir}/../.metrics.json',
            "data": f'{self.outdir}/../.data.json'
        }
        self.content_dict = {}
        for slot, path in self.path_dict.items():
            if not os.path.exists(path):
                self.content_dict[slot] = {}
            else:
                with open(path) as f:
                    self.content_dict[slot] = json.load(f)
        self.env = Environment(
            loader=FileSystemLoader(os.path.dirname(__file__) + '/../templates/'),
            autoescape=select_autoescape(['html', 'xml'])
        )


    def add_metric(self, name, value=None, total=None, fraction=None):
        '''add metric to metric_list
        '''
        self.metric_list.append(self.Metric(
            name=name, value=value, total=total, fraction=fraction
        ))

    def get_fraction(self):
        '''
        metric_list: list of namedtuple(name, value, total, fraction)
        '''
        metric_list = []
        for metric in self.metric_list:
            fraction = metric.fraction
            if metric.total:
                fraction = metric.value / metric.total
            if fraction:
                fraction = round(fraction, 4)
            metric_list.append(self.Metric(
                name=metric.name,
                value=metric.value,
                total=metric.total,
                fraction=fraction,
            ))
        self.metric_list = metric_list

    def metric_list_to_stat(self):
        f_stat = open(self.stat_file, 'w')
        for metric in self.metric_list:
            line = f'{metric.name}: '
            value = metric.value
            fraction = metric.fraction
            if fraction:
                fraction = round(fraction * 100, 2)
            if value:
                if isinstance(value, numbers.Number):
                    line += format(value, ',')
                    if fraction:
                        line += f'({fraction}%)'
                else:
                    line += value
            elif fraction:
                line += f'{fraction}%'
            f_stat.write(line + '\n')
        f_stat.close()

    def dump_content(self, slot):
        '''dump content to json file
        '''
        with open(self.path_dict[slot], 'w') as f:
            json.dump(self.content_dict[slot], f, indent=4)

    @add_log
    def render_html(self):
        template = self.env.get_template(f'html/{self.assay}/base.html')
        report_html = f"{self.outdir}/../{self.sample}_report.html"
        with io.open(report_html, 'w', encoding='utf8') as f:
            html = template.render(self.content_dict['data'])
            f.write(html)

    def stat_to_data(self):
        df = pd.read_table(self.stat_file, header=None, sep=':', dtype=str)
        self.content_dict['data'][self.step_name + '_summary'] = df.values.tolist()

    def stat_to_metric(self):
        df = pd.read_table(self.stat_file, header=None, sep=':', dtype=str)
        dic = dict(zip(df.iloc[:, 0], df.iloc[:, 1].str.strip()))
        metrics = dict()
        for key, value in dic.items():
            bool_fraction = False
            if '%' in value:
                bool_fraction = True
            chars = [',', '%', ')']
            for c in chars:
                value = value.replace(c, '')
            fraction = None
            try:
                number, fraction = value.split('(')
            except ValueError:
                number = value
            if not number.isnumeric():
                try:
                    number = float(number)
                    if bool_fraction:
                        number = round(number / 100, 4)
                except ValueError:
                    pass
            else:
                number = int(number)
            metrics[key] = number
            if fraction:
                fraction = round(float(fraction) / 100, 4)
                metrics[key + ' Fraction'] = fraction
        self.content_dict['metric'][self.step_name + '_summary'] = metrics

    def add_content_item(self, slot, **kwargs):
        for key, value in kwargs.items():
            # if value is a dict, and some value in this dict is float, format these value
            if isinstance(value, abc.Mapping):
                for value_key, value_value in value.items():
                    if isinstance(value_value, float):
                        value[value_key] = round(value_value, 4)

            self.content_dict[slot][key] = value

    def add_data_item(self, **kwargs):
        self.add_content_item("data", **kwargs)

    @staticmethod
    def get_table(title, table_id, df_table):
        """
        return html code
        """
        table_dict = {}
        table_dict['title'] = title
        table_dict['table'] = df_table.to_html(
            escape=False,
            index=False,
            table_id=table_id,
            justify="center")
        table_dict['id'] = id
        return table_dict

    @add_log
    def clean_up(self):
        if self.metric_list:
            self.get_fraction()
            self.metric_list_to_stat()
        self.stat_to_metric()
        self.stat_to_data()
        self.dump_content(slot="data")
        self.dump_content(slot="metric")
        self.render_html()


