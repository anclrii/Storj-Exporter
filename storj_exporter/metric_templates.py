from dataclasses import dataclass, field
from prometheus_client.core import (
    GaugeMetricFamily,
    InfoMetricFamily,
    UnknownMetricFamily
)
from utils import to_float


@dataclass
class MetricTemplate(object):
    metric_name: str
    documentation: str
    data_dict: dict
    data_keys: list
    labels: list = field(default_factory=lambda: ['type'])
    extra_labels_values: list = field(default_factory=lambda: [])
    _metric_class = UnknownMetricFamily

    def _get_value(self, key):
        return self.data_dict.get(key, None)

    def _create_metric_object(self):
        return self._metric_class(
            name=self.metric_name, documentation=self.documentation, labels=self.labels)

    def get_metric_object(self):
        _metric_object = self._create_metric_object()
        if self.data_dict:
            self._add_metric_samples(_metric_object)
        return _metric_object

    def _add_metric_samples(self, _metric_object):
        for key in self.data_keys:
            value = self._get_value(key)
            labels_list = [key] + self.extra_labels_values
            if labels_list and value is not None:
                _metric_object.add_metric(labels_list, value)


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

    def _create_metric_object(self):
        return InfoMetricFamily(
            name=self.metric_name, documentation=self.documentation, labels=self.labels)

    def _get_value(self, key):
        value = self.data_dict.get(key, None)
        if value is not None:
            value = {key: str(value)}
        return value
