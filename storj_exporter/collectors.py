from metric_templates import GaugeMetricTemplate, InfoMetricTemplate
from utils import sum_list_of_dicts, safe_list_get


class StorjCollector(object):
    def __init__(self, client):
        self.client = client
        self._refresh_data()

    def _refresh_data(self):
        pass

    def collect(self):
        pass

    def _get_metric_template_map(self):
        pass


class NodeCollector(StorjCollector):
    def _refresh_data(self):
        self._node = self.client.node()

    def collect(self):
        self._refresh_data()
        _metric_template_map = self._get_metric_template_map()
        for template in _metric_template_map:
            yield template.get_metric_object()

    def _get_metric_template_map(self):
        _diskSpace = self._node.get('diskSpace', None)
        _bandwidth = self._node.get('bandwidth', None)
        _metric_template_map = [
            InfoMetricTemplate(
                metric_name='storj_node',
                documentation='Storj node info',
                data_dict=self._node,
                data_keys=['nodeID', 'wallet', 'lastPinged', 'upToDate', 'version',
                           'allowedVersion', 'startedAt']
            ),
            GaugeMetricTemplate(
                metric_name='storj_total_diskspace',
                documentation='Storj total diskspace metrics',
                data_dict=_diskSpace,
                data_keys=['used', 'available', 'trash']
            ),
            GaugeMetricTemplate(
                metric_name='storj_total_bandwidth',
                documentation='Storj total bandwidth metrics',
                data_dict=_bandwidth,
                data_keys=['used', 'available']
            ),
        ]
        return _metric_template_map


class SatCollector(StorjCollector):
    def _refresh_data(self):
        self._node = self.client.node()

    def collect(self):
        self._refresh_data()
        self._node = self.client.node()
        for satellite in self._node.get('satellites', []):
            try:
                _sat_id = satellite.get('id', None)
                _sat_url = satellite.get('url', None)
                if not _sat_id or not _sat_url:
                    continue
                _sat_data = self.client.satellite(_sat_id)
                _suspended = 1 if satellite.get('suspended', None) else 0
                _sat_data.update({'suspended': _suspended})
                _disqualified = 1 if satellite.get('disqualified', None) else 0
                _sat_data.update({'disqualified': _disqualified})
                _metric_template_map = self._get_metric_template_map(
                    _sat_data, _sat_id, _sat_url)
                for template in _metric_template_map:
                    yield template.get_metric_object()
            except Exception:
                pass

    def _get_metric_template_map(self, _sat_data, _sat_id, _sat_url):
        _month_ingress = sum_list_of_dicts(
            _sat_data.get('bandwidthDaily', {}), "ingress")
        _month_egress = sum_list_of_dicts(
            _sat_data.get('bandwidthDaily', {}), "egress")
        _day_bandwidth = safe_list_get(_sat_data.get('bandwidthDaily', [{}]), -1)
        _day_storage = safe_list_get(_sat_data.get('storageDaily', None), -1)
        _audits = _sat_data.get('audits', None)

        _metric_template_map = [
            GaugeMetricTemplate(
                metric_name='storj_sat_summary',
                documentation='Storj satellite summary metrics',
                data_dict=_sat_data,
                data_keys=['storageSummary', 'bandwidthSummary', 'egressSummary',
                            'ingressSummary', 'currentStorageUsed', 'disqualified',
                            'suspended'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_audit',
                documentation='Storj satellite audit metrics',
                data_dict=_audits,
                data_keys=['auditScore', 'suspensionScore', 'onlineScore'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_month_egress',
                documentation='Storj satellite egress since current month start',
                data_dict=_month_egress,
                data_keys=['repair', 'audit', 'usage'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_month_ingress',
                documentation='Storj satellite ingress since current month start',
                data_dict=_month_ingress,
                data_keys=['repair', 'usage'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_day_egress',
                documentation='Storj satellite egress since current day start',
                data_dict=_day_bandwidth,
                data_keys=['repair', 'audit', 'usage'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_day_ingress',
                documentation='Storj satellite ingress since current day start',
                data_dict=_day_bandwidth,
                data_keys=['repair', 'usage'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_day_storage',
                documentation='Storj satellite data stored on disk since current '
                              'day start',
                data_dict=_day_storage,
                data_keys=['atRestTotal'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
        ]
        return _metric_template_map


class PayoutCollector(StorjCollector):
    def _refresh_data(self):
        self._payout = self.client.payout().get('currentMonth', {})

    def collect(self):
        self._refresh_data()
        _metric_template_map = self._get_metric_template_map()
        for template in _metric_template_map:
            yield template.get_metric_object()

    def _get_metric_template_map(self):
        _metric_template_map = [
            GaugeMetricTemplate(
                metric_name='storj_payout_currentMonth',
                documentation='Storj estimated payouts for current month',
                data_dict=self._payout,
                data_keys=['egressBandwidth', 'egressBandwidthPayout',
                           'egressRepairAudit', 'egressRepairAuditPayout',
                           'diskSpace', 'diskSpacePayout', 'heldRate', 'payout',
                           'held'],
            ),
        ]
        return _metric_template_map
