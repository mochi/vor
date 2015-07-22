"""
Tests for L{vor.graphite}.
"""

from twisted.trial import unittest

from vor.graphite import sanitizeMetric, sanitizeMetricElement

class SanitizeMetricTests(unittest.TestCase):
    """
    Tests for L{sanitizeMetric}.
    """

    def test_spaces(self):
        """
        Spaces are replaced by underscores.
        """
        self.assertEqual(b'some_spaced_name',
                         sanitizeMetric(u'some spaced name'))

    def test_slashes(self):
        """
        Slashes are replaced by dashes.
        """
        self.assertEqual(b'some-slashed-name',
                         sanitizeMetric(u'some/slashed/name'))

    def test_others(self):
        """
        Special characters are removed.
        """
        self.assertEqual(b'somename',
                         sanitizeMetric(u'some[name]'))

    def test_dots(self):
        """
        A metric with dots is left unchanged.
        """
        self.assertEqual(b'example.org',
                         sanitizeMetric(u'example.org'))



class SanitizeMetricElementTests(unittest.TestCase):
    """
    Tests for L{sanitizeMetricElement}.
    """

    def test_dots(self):
        """
        Dots are replaced by underscores.
        """
        self.assertEqual(b'example_org',
                         sanitizeMetricElement(u'example.org'))


    def test_others(self):
        """
        Other special characters are replaced as L{sanitizeMetric}.
        """
        self.assertEqual(b'http--example_org-',
                         sanitizeMetricElement(u'http://example.org/'))
