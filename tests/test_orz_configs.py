from unittest import TestCase
from itertools import combinations, chain
from ORZ.configs import GetsByConfig, Config, CacheConfigMgr, ConfigColl

class TestGetsByConfigs(TestCase):
    def test_hash_keys(self):
        keys = ['a', 'b', 'c', 'd']
        config = Config('111', keys)
        cfg = GetsByConfig(config, ('c',))
        self.assertEqual(cfg.as_key(), tuple(sorted(config.as_key()+(cfg.order,))))

    def test_to_strings(self):
        kw = {'a':1, 'b':2}
        cfg = GetsByConfig(Config('111', kw.keys()), ('a', ))
        self.assertEqual(cfg.to_string(kw), '111:a=1|b=2|order_by:a')


class TestConfigMgr(TestCase):
    def setUp(self):
        self.config = Config("11111", ("a", "b"))
        self.gets_by_config = GetsByConfig(self.config, ("a", ))

    def test_add(self):
        mgr = CacheConfigMgr()
        mgr.add_to(mgr.normal_config_coll, self.config)
        self.assertEqual(len(mgr.normal_config_coll), 1)
        self.assertEqual(mgr.normal_config_coll[self.config.as_key()], self.config)

        mgr.add_to(mgr.gets_by_config_coll, self.gets_by_config)
        self.assertEqual(len(mgr.normal_config_coll), 1)
        self.assertEqual(len(mgr.gets_by_config_coll), 1)
        self.assertEqual(mgr.gets_by_config_coll[self.gets_by_config.as_key()], self.gets_by_config)

    def test_lookup(self):
        mgr = CacheConfigMgr()
        mgr.add_to(mgr.normal_config_coll, self.config)
        mgr.add_to(mgr.gets_by_config_coll, self.gets_by_config)

        self.assertEqual(mgr.lookup_normal(("b", "a")) , self.config)
        self.assertEqual(mgr.lookup_gets_by(("b", "a"), ("a", )) , self.gets_by_config)

    def test_gen_basic_configs(self):
        sort_ = lambda x: sorted(x, key= lambda x:''.join(x))
        keys = [ "a", "b", "c", "id" ]
        mgr = CacheConfigMgr()
        mgr.generate_basic_configs('1111', keys, list((i, ) for i in keys))

        self.assertEqual(len(mgr.normal_config_coll), 8)
        self.assertEqual(len(mgr.gets_by_config_coll), 8*4)

        key_combs = list(chain(*[combinations(keys[:3], i) for i in range(1, 4)]))+[("id",)]

        self.assertEqual(sort_(mgr.normal_config_coll.keys()), sort_(key_combs))

        key_combs_with_order = [k+("order_by:"+i, ) for k in key_combs for i in keys]
        self.assertEqual(sort_(mgr.gets_by_config_coll.keys()), sort_(key_combs_with_order))

    def test_lookup_related(self):
        sort_ = lambda x: sorted(x, key= lambda x:''.join(x))
        keys = ["a", "b", "id"]
        mgr = CacheConfigMgr()
        mgr.generate_basic_configs('1111', keys)
        cfgs = mgr.lookup_related("a")
        predate_configs = [c for c in mgr.items() if "a" in c.keys]
        self.assertEqual(sort_([i.as_key() for i in cfgs]),
                         sort_([i.as_key() for i in predate_configs]))


        mgr.generate_basic_configs('1112', keys, (('c', 'b'),))
        cfgs = mgr.lookup_related("c")
        predate_configs = [c for c in mgr.items() if "c" in c.keys]
        self.assertEqual(sort_([i.as_key() for i in cfgs]),
                         sort_([i.as_key() for i in predate_configs]))


class TestConfigColl(TestCase):
    def test_main(self):
        coll = ConfigColl()
        coll['1'] = 1
        self.assertEqual(coll['1'], 1)
        self.assertEqual(coll['2'], None)
