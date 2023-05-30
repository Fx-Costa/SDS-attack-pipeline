import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from Utils.SamplerUtil import SamplerUtil


class TestSamplerUtil(unittest.TestCase):
    def setUp(self):
        self.sampler = SamplerUtil()

    @patch('SamplerUtil.ConfigUtil.instance')
    @patch('SamplerUtil.LoggerUtil.instance')
    def test_sample_with_n_and_m(self, mock_logger, mock_config):
        mock_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_config.__getitem__.side_effect = lambda x: \
        {"LOGGING": {"format": "%(message)s", "date_format": "%Y-%m-%d"}}[x]

        # Mocking the read_csv function and returning a DataFrame with 10 rows and 5 columns
        with patch.object(pd, 'read_csv', return_value=pd.DataFrame(index=range(10), columns=range(5))):
            result = self.sampler.sample(n=3, m=2)
            self.assertEqual(result.shape, (3, 2))

    @patch('SamplerUtil.logger')
    def test_sample_with_n_only(self, mock_logger):
        # Mocking the read_csv function and returning a DataFrame with 10 rows and 5 columns
        with patch.object(pd, 'read_csv', return_value=pd.DataFrame(index=range(10), columns=range(5))):
            result = self.sampler.sample(n=3)
            self.assertEqual(result.shape, (3, 5))

    @patch('SamplerUtil.logger')
    def test_sample_with_cols(self, mock_logger):
        # Mocking the read_csv function and returning a DataFrame with 10 rows and 5 columns
        with patch.object(pd, 'read_csv', return_value=pd.DataFrame(index=range(10), columns=range(5))):
            result = self.sampler.sample(cols=[0, 2, 4])
            self.assertEqual(result.shape, (10, 3))

    @patch('SamplerUtil.logger')
    def test_sample_with_invalid_m_and_cols(self, mock_logger):
        # Mocking the read_csv function and returning a DataFrame with 10 rows and 5 columns
        with patch.object(pd, 'read_csv', return_value=pd.DataFrame(index=range(10), columns=range(5))):
            with self.assertRaises(ValueError):
                self.sampler.sample(m=3, cols=[0, 1])

    @patch('SamplerUtil.logger')
    def test_sample_with_invalid_n(self, mock_logger):
        # Mocking the read_csv function and returning a DataFrame with 10 rows and 5 columns
        with patch.object(pd, 'read_csv', return_value=pd.DataFrame(index=range(10), columns=range(5))):
            with self.assertRaises(ValueError):
                self.sampler.sample(n=0)


if __name__ == '__main__':
    unittest.main()
