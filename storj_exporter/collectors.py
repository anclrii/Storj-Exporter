import logging
from metric_templates import GaugeMetricTemplate, InfoMetricTemplate
from utils import sum_list_of_dicts, safe_list_get

logger = logging.getLogger(__name__)


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
        logger.debug(f'{self.__class__.__name__}.collect() called, refreshing data ...')
        self._refresh_data()
        logger.debug(f'Creating metrics objects for {self.__class__.__name__}')
        _metric_template_map = self._get_metric_template_map()
        for template in _metric_template_map:
            template.add_metric_samples()
            yield template.metric_object

    def _get_metric_template_map(self):
        _diskSpace = self._node.get('diskSpace', None)
        _bandwidth = self._node.get('bandwidth', None)
        _metric_template_map = [
            InfoMetricTemplate(
                metric_name='storj_node',
                documentation='Storj node info',
                data_dict=self._node,
                data_keys=['nodeID', 'wallet', 'upToDate', 'version',
                           'allowedVersion', 'quicStatus']
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
        logger.debug(f'{self.__class__.__name__}.collect() called, refreshing data ...')
        self._refresh_data()
        logger.debug(f'Creating metrics objects for {self.__class__.__name__}')
        _metric_template_map = self._get_metric_template_map({}, 'id', 'url')
        for satellite in self._node.get('satellites', []):
            logger.debug(f'Processing satellite {satellite}')
            if satellite and isinstance(satellite, dict):
                _sat_data, _sat_id, _sat_url = self._get_sat_data(satellite)
                for template in _metric_template_map:
                    template.data_dict = _sat_data
                    template.extra_labels_values = [_sat_id, _sat_url]
                    template.add_metric_samples()
            else:
                logger.debug('Node data for satellite is invalid, skipping satellite')
        for template in _metric_template_map:
            yield template.metric_object

    def _get_sat_data(self, satellite):
        _sat_data = {}
        _sat_id = satellite.get('id', None)
        _sat_url = satellite.get('url', None)
        if _sat_id and _sat_url:
            logger.debug(f'Getting data for satellite {_sat_url} ({_sat_id})')
            _sat_data = self.client.satellite(_sat_id)
            if _sat_data and isinstance(_sat_data, dict):
                _sat_data = self._prepare_sat_data(satellite, _sat_data)
            else:
                logger.debug('Satellite data is invalid, skipping satellite')
        else:
            logger.debug(f'_sat_id = {_sat_id} and _sat_url = {_sat_url}, '
                         'skipping satellite ...')
        return _sat_data, _sat_id, _sat_url

    def _prepare_sat_data(self, satellite, _sat_data):
        logger.debug('Preparing satellite data for adding samples ...')
        _suspended = 1 if satellite.get('suspended', None) else 0
        _sat_data.update({'suspended': _suspended})

        _disqualified = 1 if satellite.get('disqualified', None) else 0
        _sat_data.update({'disqualified': _disqualified})

        _month_ingress = sum_list_of_dicts(
            _sat_data.get('bandwidthDaily', {}), "ingress")
        _sat_data.update({'month_ingress': _month_ingress})

        _month_egress = sum_list_of_dicts(
            _sat_data.get('bandwidthDaily', {}), "egress")
        _sat_data.update({'month_egress': _month_egress})

        _day_bandwidth = safe_list_get(_sat_data.get('bandwidthDaily', [{}]), -1)
        _sat_data.update({'day_bandwidth': _day_bandwidth})

        _day_storage = safe_list_get(_sat_data.get('storageDaily', None), -1)
        _sat_data.update({'day_storage': _day_storage})
        return _sat_data

    def _get_metric_template_map(self, _sat_data, _sat_id, _sat_url):
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
                data_dict=_sat_data,
                nested_path=['audits'],
                data_keys=['auditScore', 'suspensionScore', 'onlineScore'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_month_egress',
                documentation='Storj satellite egress since current month start',
                data_dict=_sat_data,
                nested_path=['month_egress'],
                data_keys=['repair', 'audit', 'usage'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_month_ingress',
                documentation='Storj satellite ingress since current month start',
                data_dict=_sat_data,
                nested_path=['month_ingress'],
                data_keys=['repair', 'usage'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
            GaugeMetricTemplate(
                metric_name='storj_sat_day_storage',
                documentation='Storj satellite data stored on disk since current '
                              'day start',
                data_dict=_sat_data,
                nested_path=['day_storage'],
                data_keys=['atRestTotal'],
                labels=['type', 'satellite', 'url'],
                extra_labels_values=[_sat_id, _sat_url]
            ),
        ]
        return _metric_template_map


class PayoutCollector(StorjCollector):
    def _refresh_data(self):
        self._payout = self.client.payout()

    def collect(self):
        logger.debug(f'{self.__class__.__name__}.collect() called, refreshing data ...')
        self._refresh_data()
        logger.debug(f'Creating metrics objects for {self.__class__.__name__}')
        _metric_template_map = self._get_metric_template_map()
        for template in _metric_template_map:
            template.add_metric_samples()
            yield template.metric_object

    def _get_metric_template_map(self):
        _payout_data = self._payout.get('currentMonth', {})
        _payout_data['currentMonthExpectations'] = self._payout.get(
            'currentMonthExpectations', None)
        _metric_template_map = [
            GaugeMetricTemplate(
                metric_name='storj_payout_currentMonth',
                documentation='Storj estimated payouts for current month',
                data_dict=_payout_data,
                data_keys=['egressBandwidth', 'egressBandwidthPayout',
                           'egressRepairAudit', 'egressRepairAuditPayout',
                           'diskSpace', 'diskSpacePayout', 'heldRate', 'payout',
                           'held', 'currentMonthExpectations'],
            ),
        ]
        return _metric_template_map
