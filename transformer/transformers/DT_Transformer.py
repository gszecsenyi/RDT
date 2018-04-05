import exrex
import itertools
import numpy as np
import pandas as pd
import time
import pdb
import json
import os.path as op
import sys

from BaseTransformer import *
from dateutil import parser

class DT_Transformer(BaseTransformer):
	""" 
	This class represents the datetime transformer for SDV 
	"""

	def __init__(self):
		""" initialize transformer """
		super(DT_Transformer, self).__init__()
		self.type = 'datetime'

	def fit_transform(self, col, col_meta):
		""" Returns a tuple (transformed_table, new_table_meta) """
		out = pd.DataFrame(columns=[])
		col_name = col_meta['name']
		out[col_name] = col.apply(self.get_val)

		# replace missing values
		# create an extra column for missing values if they exist in the data
		new_name = '?' + col_name
		# if are just processing child rows, then the name is already known
		out[new_name] = pd.notnull(col) * 1
		return out

	def transform(self, col, col_meta):
		""" Does the required transformations to the data """
		return self.fit_transform(col, col_meta)

	def reverse_transform(self, col, col_meta):
		""" Converts data back into original format """
		output = pd.DataFrame(columns=[])
		date_format = col_meta['format']
		col_name = col_meta['name']
		fn = self.get_date_converter(col_name, date_format)
		data = col.to_frame()
		output[col_name] = data.apply(fn, axis=1)
		return output

	def get_val(self, x):
		""" Converts datetime to number """
		try:
			tmp = parser.parse(str(x)).timetuple()
			return time.mktime(tmp)*1e9
		except (ValueError, AttributeError, TypeError):
			# if we return pd.NaT, pandas will exclude the column
			# when calculating covariance, so just use np.nan
			return np.nan

	def get_date_converter(self, col, meta):
		'''Returns a converter that takes in an integer representing ms
		   and turns it into a string date

		:param col: name of column
		:type col: str
		:param missing: true if column has NULL values
		:type missing: bool
		:param meta: type of column values
		:type meta: str

		:returns: function
		'''

		def safe_date(x):
			if '?' + col in x:
				print('hey')
				missing = True
			else:
				missing = False

			if missing and x['?' + col] == 0:
				return np.nan
			# TODO: Figure out right way to check missing
			t = x[col]
			try:
				if np.isnan(t):
					return np.nan
			except:
				print(t)
			tmp = time.gmtime(float(t)/1e9)
			return time.strftime(meta, tmp)

		return safe_date