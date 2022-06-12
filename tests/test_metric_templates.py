import pytest
from storj_exporter.metric_templates import (
    MetricTemplate,
    InfoMetricTemplate,
    GaugeMetricTemplate
)
from prometheus_client.core import (
    GaugeMetricFamily,
    InfoMetricFamily,
    UnknownMetricFamily
)


class TestMetricTemplate:
    def test_init(self):
        template = MetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': 1.1},
            data_keys=['test_key'],
            labels=['label1', 'label2'],
            extra_labels_values=['label2_value']
        )
        assert template.metric_name == 'test_metric_name'
        assert template.documentation == 'test_documentation'
        assert template.data_dict == {'test_key': 1.1}
        assert template.data_keys == ['test_key']
        assert template.labels == ['label1', 'label2']
        assert template.extra_labels_values == ['label2_value']
        assert type(template.metric_object) == UnknownMetricFamily
        assert template.metric_object.name == 'test_metric_name'
        assert template.metric_object.documentation == 'test_documentation'
        assert len(template.metric_object.samples) == 0

    def test_init_defaults(self):
        gauge_template = MetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': 'test_value'},
            data_keys=['test_key']
        )
        assert gauge_template.metric_name == 'test_metric_name'
        assert gauge_template.documentation == 'test_documentation'
        assert gauge_template.data_dict == {'test_key': 'test_value'}
        assert gauge_template.data_keys == ['test_key']
        assert gauge_template.labels == ['type']
        assert gauge_template.extra_labels_values == []

    def test_get_value(self):
        metric_template = MetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': 1.1},
            data_keys=['test_key'],
        )
        value = metric_template._get_value('test_key')
        assert value == 1.1

    def test_template_metric_object(self):
        metric_template = MetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': 1.1},
            data_keys=['test_key'],
            labels=['label1', 'label2'],
            extra_labels_values=['label2_value']
        )
        metric_template.add_metric_samples()
        metric_object = metric_template.metric_object
        assert type(metric_object) == UnknownMetricFamily
        assert metric_object.name == 'test_metric_name'
        assert metric_object.documentation == 'test_documentation'
        assert len(metric_object.samples) == 1
        assert metric_object.samples[0].labels == {
            'label1': 'test_key', 'label2': 'label2_value'}
        assert metric_object.samples[0].value == 1.1

    def test_template_metric_object_none_value(self):
        metric_template = MetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': None},
            data_keys=['test_key']
        )
        metric_template.add_metric_samples()
        metric_object = metric_template.metric_object
        assert type(metric_object) == UnknownMetricFamily
        assert metric_object.name == 'test_metric_name'
        assert len(metric_object.samples) == 0

    @pytest.mark.parametrize('value, expected_samples', [(1.1, 1), (None, 0)])
    @pytest.mark.parametrize('extra_labels_values, expected_labels', [
        (['l2_value'], {'l1': 'test_key', 'l2': 'l2_value'}),
        ([], {'l1': 'test_key'}),
    ])
    def test_add_metric_samples(self, value, extra_labels_values, expected_samples,
                                expected_labels):
        metric_template = MetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': value},
            data_keys=['test_key'],
            labels=['l1', 'l2'],
            extra_labels_values=extra_labels_values
        )
        metric_template.add_metric_samples()
        metric_object = metric_template.metric_object
        assert len(metric_object.samples) == expected_samples
        if expected_samples > 0:
            assert metric_object.samples[0].labels == expected_labels


class TestGaugeMetricTemplate(object):
    @pytest.mark.parametrize('value, expected', [
        (1.1, 1.1),
        ('1.1', 1.1),
        (0, 0.0),
        (True, 1.0),
        (None, None),
        ('test', None),
        ('', None)
    ])
    def test_get_value(self, value, expected):
        metric_template = GaugeMetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': value},
            data_keys=['test_key'],
        )
        assert metric_template._get_value('test_key') == expected

    def test_get_metric_object(self):
        metric_template = GaugeMetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': 1.1},
            data_keys=['test_key'],
            labels=['label1', 'label2'],
            extra_labels_values=['label2_value']
        )
        metric_template.add_metric_samples()
        metric_object = metric_template.metric_object
        assert type(metric_object) == GaugeMetricFamily
        assert metric_object.name == 'test_metric_name'
        assert metric_object.documentation == 'test_documentation'
        assert len(metric_object.samples) == 1
        assert metric_object.samples[0].labels == {
            'label1': 'test_key', 'label2': 'label2_value'}
        assert metric_object.samples[0].value == 1.1


class TestInfoMetricTemplate(object):
    @pytest.mark.parametrize('value, expected', [
        ('test', {'test_key': 'test'}),
        ('1.1', {'test_key': '1.1'}),
        ('', {'test_key': ''}),
        (True, {'test_key': 'True'}),
        (1.1, {'test_key': '1.1'}),
        (0, {'test_key': '0'}),
        (None, None)
    ])
    def test_get_value(self, value, expected):
        metric_template = InfoMetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': value},
            data_keys=['test_key'],
        )
        assert metric_template._get_value('test_key') == expected

    def test_get_metric_object(self):
        metric_template = InfoMetricTemplate(
            metric_name='test_metric_name',
            documentation='test_documentation',
            data_dict={'test_key': 1.1},
            data_keys=['test_key'],
            labels=['label1', 'label2'],
            extra_labels_values=['label2_value']
        )
        metric_template.add_metric_samples()
        metric_object = metric_template.metric_object
        assert type(metric_object) == InfoMetricFamily
        assert metric_object.name == 'test_metric_name'
        assert metric_object.documentation == 'test_documentation'
        assert len(metric_object.samples) == 1
        assert metric_object.samples[0].labels == {
            'label1': 'test_key', 'label2': 'label2_value', 'test_key': '1.1'}
        assert metric_object.samples[0].value == 1
