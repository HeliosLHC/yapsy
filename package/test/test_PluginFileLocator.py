# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

from . import test_settings
import unittest
import os
from configparser import ConfigParser
from io import StringIO

import yapsy
from yapsy import PLUGIN_NAME_FORBIDEN_STRING
from yapsy.PluginManager import PluginManager
from yapsy.PluginManager import IPlugin
from yapsy.IPluginLocator import IPluginLocator
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.PluginFileLocator import PluginFileAnalyzerWithInfoFile
from yapsy.PluginFileLocator import PluginFileAnalyzerMathingRegex


	
class PluginFileAnalyzerWithInfoFileTest(unittest.TestCase):
	"""
	Test that the "info file" analyzer enforces the correct policy.
	"""
	
	def setUp(self):
		"""
		init
		"""
		self.plugin_directory  = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"plugins")
		self.yapsy_plugin_path = os.path.join(self.plugin_directory,"simpleplugin.yapsy-plugin")
		self.version_plugin_path = os.path.join(self.plugin_directory,"versioned11.version-plugin")
		self.yapsy_filter_plugin_path = os.path.join(self.plugin_directory,"simpleplugin.yapsy-filter-plugin")

	def test_Contruction(self):
		analyzer = PluginFileAnalyzerWithInfoFile("mouf")
		self.assertEqual(analyzer.name,"mouf")
	
	def test_isValid(self):
		analyzer = PluginFileAnalyzerWithInfoFile("mouf")
		self.assertTrue(analyzer.isValidPlugin(self.yapsy_plugin_path))
		self.assertFalse(analyzer.isValidPlugin(self.version_plugin_path))

	def test_getInfosDictFromPlugin(self):
		analyzer = PluginFileAnalyzerWithInfoFile("mouf")
		info_dict,cf_parser =  analyzer.getInfosDictFromPlugin(self.plugin_directory,
															   os.path.basename(self.yapsy_plugin_path))
		self.assertEqual(info_dict,
						 {'website': 'http://mathbench.sourceforge.net',
	                      'description': 'A simple plugin usefull for basic testing',
						  'author': 'Thibauld Nion',
						  'version': '0.1',
						  'path': '%s' % os.path.join(self.plugin_directory,"SimplePlugin"),
						  'name': 'Simple Plugin',
						  'copyright': '2014'})
		self.assertTrue(isinstance(cf_parser,ConfigParser))
		
	def test_isValid_WithMultiExtensions(self):
		analyzer = PluginFileAnalyzerWithInfoFile("mouf",("yapsy-plugin","yapsy-filter-plugin"))
		self.assertTrue(analyzer.isValidPlugin(self.yapsy_plugin_path))
		self.assertFalse(analyzer.isValidPlugin(self.version_plugin_path))
		self.assertTrue(analyzer.isValidPlugin(self.yapsy_filter_plugin_path))

	def test__extractCorePluginInfo_with_str_filename(self):
		plugin_desc_content = str("simpleplugin.yapsy-plugin")
		analyzer = PluginFileAnalyzerWithInfoFile("mouf", ("yapsy-plugin"))
		infos, parser = analyzer._extractCorePluginInfo(self.plugin_directory,
														plugin_desc_content)
		self.assertEqual("Simple Plugin", infos["name"])
		self.assertEqual(os.path.join(self.plugin_directory, "SimplePlugin"), infos["path"])
		
	def test__extractCorePluginInfo_with_minimal_description(self):
		plugin_desc_content = StringIO("""\
[Core]
Name = Simple Plugin
Module = SimplePlugin
""")
		analyzer = PluginFileAnalyzerWithInfoFile("mouf",
												  ("yapsy-plugin"))
		infos, parser = analyzer._extractCorePluginInfo("bla",plugin_desc_content)
		self.assertEqual("Simple Plugin", infos["name"])
		self.assertEqual(os.path.join("bla","SimplePlugin"), infos["path"])
		self.assertTrue(isinstance(parser,ConfigParser))
		
	def test_getPluginNameAndModuleFromStream_with_invalid_descriptions(self):
		plugin_desc_content = StringIO("""\
[Core]
Name = Bla{0}Bli
Module = SimplePlugin
""".format(PLUGIN_NAME_FORBIDEN_STRING))
		analyzer = PluginFileAnalyzerWithInfoFile("mouf",
												  ("yapsy-plugin"))
		res = analyzer._extractCorePluginInfo("bla",plugin_desc_content)
		self.assertEqual((None, None), res)
		plugin_desc_content = StringIO("""\
[Core]
Name = Simple Plugin
""")
		analyzer = PluginFileAnalyzerWithInfoFile("mouf",
												  ("yapsy-plugin"))
		res = analyzer._extractCorePluginInfo("bla",plugin_desc_content)
		self.assertEqual((None, None), res)
		plugin_desc_content = StringIO("""\
[Core]
Module = Simple Plugin
""")
		res = analyzer._extractCorePluginInfo("bla",plugin_desc_content)
		self.assertEqual((None, None), res)
		plugin_desc_content = StringIO("""\
[Mouf]
Bla = Simple Plugin
""")
		res = analyzer._extractCorePluginInfo("bla",plugin_desc_content)
		self.assertEqual((None, None), res)


class PluginFileAnalyzerMathingRegexTest(unittest.TestCase):
	"""
	Test that the "regex" analyzer enforces the correct policy.
	"""
	
	def setUp(self):
		"""
		init
		"""
		self.plugin_directory  = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"plugins")
		self.yapsy_plugin_path = os.path.join(self.plugin_directory,"SimplePlugin.py")
		self.version_plugin_10_path = os.path.join(self.plugin_directory,"VersionedPlugin10.py")
		self.version_plugin_12_path = os.path.join(self.plugin_directory,"VersionedPlugin12.py")

	def test_Contruction(self):
		analyzer = PluginFileAnalyzerMathingRegex("mouf",".*")
		self.assertEqual(analyzer.name,"mouf")
	
	def test_isValid(self):
		analyzer = PluginFileAnalyzerMathingRegex("mouf",r".*VersionedPlugin\d+\.py$")
		self.assertFalse(analyzer.isValidPlugin(self.yapsy_plugin_path))
		self.assertTrue(analyzer.isValidPlugin(self.version_plugin_10_path))
		self.assertTrue(analyzer.isValidPlugin(self.version_plugin_12_path))

	def test_getInfosDictFromPlugin(self):
		analyzer = PluginFileAnalyzerMathingRegex("mouf",r".*VersionedPlugin\d+\.py$")
		info_dict,cf_parser =  analyzer.getInfosDictFromPlugin(self.plugin_directory,
															   os.path.basename(self.version_plugin_10_path))
		self.assertEqual(info_dict,{'path': self.version_plugin_10_path, 'name': 'VersionedPlugin10'})
		self.assertTrue(isinstance(cf_parser,ConfigParser))

class PluginFileLocatorTest(unittest.TestCase):
	"""
	Test that the "file" locator.
	"""
	
	def setUp(self):
		"""
		init
		"""
		self.plugin_directory  = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"plugins")
		self.plugin_as_dir_directory  = os.path.join(
			os.path.dirname(os.path.abspath(__file__)),
			"pluginsasdirs")
		self.plugin_info_file = "simpleplugin.yapsy-plugin"
		self.plugin_name = "SimplePlugin"
		self.plugin_impl_file = self.plugin_name+".py"
		
	def test_default_plugins_place_is_parent_dir(self):
		"""Test a non-trivial default behaviour introduced some time ago :S"""
		pl = PluginFileLocator()
		expected_yapsy_module_path = os.path.dirname(yapsy.__file__)
		first_plugin_place = pl.plugins_places[0]
		self.assertEqual(expected_yapsy_module_path, first_plugin_place)
	
	
	def test_gatherCorePluginInfo(self):
		pl = PluginFileLocator()
		plugin_info,cf_parser = pl.gatherCorePluginInfo(self.plugin_directory,"simpleplugin.yapsy-plugin")
		self.assertTrue(plugin_info.name,"Simple Plugin")
		self.assertTrue(isinstance(cf_parser,ConfigParser))
		plugin_info,cf_parser = pl.gatherCorePluginInfo(self.plugin_directory,"notaplugin.atall")
		self.assertEqual(plugin_info,None)
		self.assertEqual(cf_parser,None)
		
		

class PluginManagerSetUpTest(unittest.TestCase):

	def test_default_init(self):
		pm = PluginManager()
		self.assertEqual(["Default"],pm.getCategories())
		self.assertTrue(isinstance(pm.getPluginLocator(),PluginFileLocator))
	
	def test_init_with_category_filter(self):
		pm = PluginManager(categories_filter={"Mouf": IPlugin})
		self.assertEqual(["Mouf"],pm.getCategories())
		self.assertTrue(isinstance(pm.getPluginLocator(),PluginFileLocator))
		
	def test_init_with_plugin_info_ext(self):
		pm = PluginManager(plugin_info_ext="bla")
		self.assertEqual(["Default"],pm.getCategories())
		self.assertTrue(isinstance(pm.getPluginLocator(),PluginFileLocator))
	
	def test_init_with_plugin_locator(self):
		class SpecificLocator(IPluginLocator):
			pass
		pm = PluginManager(plugin_locator=SpecificLocator())
		self.assertEqual(["Default"],pm.getCategories())
		self.assertTrue(isinstance(pm.getPluginLocator(),SpecificLocator))

	def test_init_with_plugin_info_ext_and_locator(self):
		class SpecificLocator(IPluginLocator):
			pass
		self.assertRaises(ValueError,
						  PluginManager,plugin_info_ext="bla",
						  plugin_locator=SpecificLocator())

	def test_getPluginCandidates_too_early(self):
		pm = PluginManager()
		self.assertRaises(RuntimeError,pm.getPluginCandidates)

		
	def test_setPluginLocator_with_invalid_locator(self):
		class SpecificLocator:
			pass
		pm = PluginManager()
		self.assertRaises(TypeError,
						  pm.setPluginLocator,SpecificLocator())


suite = unittest.TestSuite([
		unittest.TestLoader().loadTestsFromTestCase(PluginFileAnalyzerWithInfoFileTest),
		unittest.TestLoader().loadTestsFromTestCase(PluginFileAnalyzerMathingRegexTest),
		unittest.TestLoader().loadTestsFromTestCase(PluginFileLocatorTest),
		unittest.TestLoader().loadTestsFromTestCase(PluginManagerSetUpTest),
		])
