from storj_exporter.metric_templates import GaugeMetricTemplate

class TestMetricTemplates:
    def test_init(self):
        template = GaugeMetricTemplate(
            metric_name='storj_total_diskspace',
            documentation='Storj total diskspace metrics',
            data_dict={'used': 1, 'available': 2, 'trash': 3},
            data_keys=['used', 'available', 'trash']
        )
        assert template.metric_name == 'storj_total_diskspace'
        assert template.documentation == 'Storj total diskspace metrics'
        assert template.data_dict == {'used': 1, 'available': 2, 'trash': 3}
        assert template.data_keys == ['used', 'available', 'trash']

    def test_get_metric_object(self):
        template = GaugeMetricTemplate(
            metric_name='storj_total_diskspace',
            documentation='Storj total diskspace metrics',
            data_dict={'used': 1, 'available': 2, 'trash': 3},
            data_keys=['used', 'available', 'trash']
        )
        metric_object = template.get_metric_object()
        assert metric_object.name == 'storj_total_diskspace'
        assert metric_object.documentation == 'Storj total diskspace metrics'




# class TestStorjCollector:
#     @pytest.mark.usefixtures("mock_get_sno")
#     @pytest.mark.parametrize("mock_get_sno",
#                              [("success"), ("missingkeys"), ("timeout")],
#                              indirect=True)
#     def test_collect_metric_map(self, client):
#         node_metric_map = NodeCollector(client)._gen_node_metric_map()
#         result = StorjCollector(client)._collect_metric_map(node_metric_map)
#         res_list = list(result)
#         assert len(res_list) == len(NodeCollector(client)._gen_node_metric_map())

#     @pytest.mark.usefixtures("mock_get_sno")
#     @pytest.mark.parametrize("mock_get_sno, expected_samples",
#                              [("success", 3), ("missingkeys", 0), ("timeout", 0)],
#                              indirect=['mock_get_sno'])
#     def test_add_metric_data(self, client, expected_samples):
#         node_metric_map = NodeCollector(client)._gen_node_metric_map()
#         metric = node_metric_map['storj_total_diskspace']
#         result = StorjCollector(client)._add_metric_data(metric)
#         assert result.name == 'storj_total_diskspace'
#         assert result.documentation == 'Storj total diskspace metrics'
#         assert len(result.samples) == expected_samples

#     @pytest.mark.parametrize("key, expected_labels, expected_value", [
#         ("used", 1, 42),
#         ("missing", 0, 0.0)])
#     def test_get_metric_values(self, gauge_dict, client, key, expected_labels,
#                                expected_value):
#         labels_list, value = StorjCollector._get_metric_values(
#             StorjCollector(client), gauge_dict, 'gauge', key)
#         assert len(labels_list) == expected_labels
#         assert value == expected_value

#     @pytest.mark.parametrize("key, expected_value", [
#         ("used", 42),
#         ("missing", 0.0)])
#     def test_get_metric_value(self, gauge_dict, key, expected_value):
#         value = StorjCollector._get_metric_value(gauge_dict, 'gauge', key)
#         assert value == expected_value

