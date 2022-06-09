from dataclasses import dataclass, field
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily

@dataclass
class MetricTemplate(object):
    metric_name: str
    documentation: str
    data_dict: dict = field(default_factory=lambda: {})
    data_keys: list = field(default_factory=lambda: [])
    labels: list = field(default_factory=lambda: ['type'])
    extra_labels: list = field(default_factory=lambda: [])

    def get_metric_object(self):
        _metric_object = self._create_metric_object()
        if self.data_dict:
            self._add_metric_samples(_metric_object)
        return _metric_object

    def _create_metric_object(self):
        return InfoMetricFamily(
            name=self.metric_name, documentation=self.documentation, labels=self.labels)

    def _add_metric_samples(self, _metric_object):
        for key in self.data_keys:
            value = self._get_value(key)
            labels_list = [key] + self.extra_labels
            if labels_list and (value or value == 0):
                _metric_object.add_metric(labels_list, value)

    def _get_value(self, key):
        return self.data_dict.get(key, None)


@dataclass
class GaugeMetricTemplate(MetricTemplate):
    def _create_metric_object(self):
        return GaugeMetricFamily(
            name=self.metric_name, documentation=self.documentation, labels=self.labels)

    def _get_value(self, key):
        return self.data_dict.get(key, None)


@dataclass
class InfoMetricTemplate(MetricTemplate):
    def _create_metric_object(self):
        return InfoMetricFamily(
            name=self.metric_name, documentation=self.documentation, labels=self.labels)

    def _get_value(self, key):
        value = self.data_dict.get(key, None)
        return {key: str(value)} if value else None
