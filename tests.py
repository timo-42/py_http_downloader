#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 18:00:20 2019

@author: kenobi
"""

import unittest
from pathlib import Path
import main

class TestUrlSanityCheck(unittest.TestCase):
    """
    Testing the url sanity checker
    """
    
    def test_scheme(self):
        (check, _) = main.url_sanity_check("https://example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, True)
        (check, _) = main.url_sanity_check("http://example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, True)
        (check, _) = main.url_sanity_check("example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("://example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("http:://example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, False)        
        (check, _) = main.url_sanity_check("irc://example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("ftp://example.com/file1.jpg", Path("/tmp"))
        self.assertEqual(check, False)
        
    def test_trailing_slash(self):
        (check, _) = main.url_sanity_check("https://example.com/file1.jpg/", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("http://example.com/", Path("/tmp"))
        self.assertEqual(check, False)   
        
    def test_missing_path(self):
        (check, _) = main.url_sanity_check("https://example.com/1", Path("/tmp"))
        self.assertEqual(check, True)
        (check, _) = main.url_sanity_check("https://example.com/", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("http://example.com", Path("/tmp"))
        self.assertEqual(check, False)   
        
    def test_path_resolving(self):
        (check, path) = main.url_sanity_check("https://example.com/a/../1.jpg", Path("/tmp"))
        self.assertEqual(check, True)
        self.assertEqual(path, Path("/tmp/example.com/1.jpg"))
        (check, _) = main.url_sanity_check("https://example.com/../../a/b/1.jpg", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("https://example.com/1", Path("/tmp"))
        self.assertEqual(check, True)
        (check, path) = main.url_sanity_check("https://example.com:1234/a/../etc/passwd", Path("/tmp"))
        self.assertEqual(check, True)
        self.assertEqual(path, Path("/tmp/example.com:1234/etc/passwd"))
        (check, path) = main.url_sanity_check("https://example.com/etc/passwd", Path("/tmp"))
        self.assertEqual(check, True)
        self.assertEqual(path, Path("/tmp/example.com/etc/passwd"))
        (check, path) = main.url_sanity_check("http://example.com:4000/a/b/../b/../../../etc/passwd", Path("/tmp"))
        self.assertEqual(check, False)
        (check, _) = main.url_sanity_check("http://example.com/a/b/../b/../../../../etc/passwd", Path("/tmp"))
        self.assertEqual(check, False)  
        
if __name__ == '__main__':
    unittest.main()