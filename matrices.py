import csv
import re
import numpy as np


def populate_adjacency_matrix(year):
	sna_ids = set()
	orpa_nrs = {}
	with open(f'{year} NO BLANKS NO BIGS SNA ID ALL FIXED Funding Data for Research SNA.csv', 'r') as data:
		reader = csv.reader(data, delimiter=',')
		next(reader)
		for row in reader:
			sna_id = row[14]
			sna_ids.add(sna_id)
			orpa_nr = row[17]
			try:
				orpa_nrs[orpa_nr].append(sna_id)
			except KeyError:
				orpa_nrs[orpa_nr] = [sna_id]
	return sna_ids, orpa_nrs




def output_adjacency_matrix(year, sna_ids, orpa_nrs):
	with open(f'{year} NO BLANKS NO BIGS SNA ID ALL FIXED Two-Mode Matrix.csv', 'w', newline='') as output:
		writer = csv.writer(output, delimiter=',')
		headers = ['SNA ID / ORPA NR']
		headers.extend(orpa_nrs.keys())
		writer.writerow(headers)
		for sna_id in sna_ids:
			row = [sna_id]
			row.extend([1 if sna_id in orpa_nr else 0 for orpa_nr in orpa_nrs.values()])
			writer.writerow(row)


def get_all_snas():
	snas = set()
	with open('All_Faculty.csv', 'r') as all_faculty:
		reader = csv.reader(all_faculty, delimiter=',')
		next(reader)
		for row in reader:
			snas.add(row[1])
	print(len(snas))
	return snas



def append_leftover_snas(year, all_snas, orpa_nrs):
	with open(f'{year} NO BLANKS NO BIGS SNA ID ALL FIXED Two-Mode Matrix.csv', 'r') as matrix,\
		open(f'ALL SNAS {year} NO BLANKS NO BIGS SNA ID ALL FIXED Two-Mode Matrix.csv', 'w', newline='') as snas:
		reader = csv.reader(matrix, delimiter=',')
		writer = csv.writer(snas, delimiter=',')
		writer.writerow(next(reader))
		snas = set()
		for row in reader:
			snas.add(row[0])
			writer.writerow(row)
		snas_not_there = all_snas - snas
		for sna in snas_not_there:
			row = [sna]
			row.extend([0 for orpa_nr in orpa_nrs.values()])
			writer.writerow(row)





def main():
	all_snas = get_all_snas()
	for year in range(2011, 2019):
		sna_ids, orpa_nrs = populate_adjacency_matrix(year)
		output_adjacency_matrix(year, sna_ids, orpa_nrs)
		append_leftover_snas(year, all_snas, orpa_nrs)


if __name__ == '__main__':
	main()