from dataclasses import dataclass, field
from prometheus_client.core import (
    GaugeMetricFamily,
    InfoMetricFamily,
    UnknownMetricFamily
)
from utils import to_float, nested_get


@dataclass
class MetricTemplate(object):
    metric_name: str
    documentation: str
    data_keys: list
    data_dict: dict = field(default_factory=lambda: {})
    nested_path: list = field(default_factory=lambda: [])
    metric_object: object = field(init=False)
    labels: list = field(default_factory=lambda: ['type'])
    extra_labels_values: list = field(default_factory=lambda: [])
    _metric_class = UnknownMetricFamily

    def __post_init__(self):
        self.metric_object = self._metric_class(
            name=self.metric_name, documentation=self.documentation, labels=self.labels)

    def _get_value(self, key):
        return self.data_dict.get(key, None)

    def add_metric_samples(self):
        if self.nested_path:
            self.data_dict = nested_get(self.data_dict, self.nested_path)
        if self.data_dict and isinstance(self.data_dict, dict):
            for key in self.data_keys:
                value = self._get_value(key)
                labels_list = [key] + self.extra_labels_values
                if labels_list and value is not None:
                    self.metric_object.add_metric(labels_list, value)
        self.data_dict = {}


@dataclass
class GaugeMetricTemplate(MetricTemplate):
    _metric_class = GaugeMetricFamily

    def _get_value(self, key):
        value = self.data_dict.get(key, None)
        if value is not None:
            value = to_float(value)
        return value


@dataclass
class InfoMetricTemplate(MetricTemplate):
    _metric_class = InfoMetricFamily

    def _get_value(self, key):
        value = self.data_dict.get(key, None)
        if value is not None:
            value = {key: str(value)}
        return value
