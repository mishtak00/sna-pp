import csv
import re
import numpy as np


def fix_names():
	with open('Funding Data for Research SNA 08292018 cos.csv', 'r') as original,\
	open('Funding Data for Research SNA 08292018 cos names fix.csv', 'w', newline='') as fixed:
		reader = csv.reader(original, delimiter=',')
		writer = csv.writer(fixed, delimiter=',')
		line = 0

		for row in reader:
			if line != 0:
				full = row[12].strip()

				# match 'last III,first'
				if re.match(r"^[\w\-'() ]+ III,[\w\-'() ]+$", full):
					full = full.split(',')
					last = full[0].strip()
					last = re.sub(' III', '', last)
					full[0] = last
					full = ','.join(full)
					row[12] = full

				# match 'last,middle_initial first'
				if re.match(r"^[\w\-'() ]+,\w \w+$", full):
					full = full.split(',')
					first = full[1].strip()
					split_first = first.split()
					mi = split_first[0]
					mi += '.'
					fn = split_first[1]
					full[1] = mi + ' ' + fn
					full = ','.join(full)
					row[12] = full

			writer.writerow(row)	
			line+=1


def process_last_name(last, first, last_counters):
	last_simple_counter, last_double_counter, last_parens_counter, last_spaced_multi_counter, last_other_counter = last_counters

	# 1-word last name
	if re.match(r"^((o|d)')*\w+$", last):
		last_simple_counter += 1
		# these are matched in the survey so they're good as is

	# 2-word-separated-by-dash last name
	elif re.match(r"^\w+-((o|d)')*\w+$", last):
		last_double_counter += 1
		# these are matched in the survey so they're good as is

	# last name and another one in parentheses
	elif re.match(r"^\w+ \(((o|d)')*\w+\)$", last):
		last_parens_counter += 1
		# turn these into 2-word-separated-by-dash form
		last = re.sub(' ', '-', re.sub('[()]', '', last))
		
	# multi word last name separated by spaces
	elif re.match(r"^(\w+ )+\w+ *$", last):
		last_spaced_multi_counter += 1
		# these are matched in the survey so they're good as is

	# other cases
	else:
		last_other_counter += 1

	last_counters = last_simple_counter, last_double_counter, last_parens_counter, last_spaced_multi_counter, last_other_counter

	return last, last_counters



def process_first_name(first, last, first_counters):
	first_simple_counter, first_init_dot_counter, first_dash_counter, first_spaced_multi_counter, first_other_counter = first_counters

	# 1-word first name
	if re.match(r"^\w+$", first):
		first_simple_counter += 1

	# initial dot space 1-word first name
	elif re.match(r"^\w\. \w+$", first):
		first_init_dot_counter += 1

	# 2-words or more first name separated by dash
	elif re.match(r"(\w+-)+\w+$", first):
		first_dash_counter += 1
	
	# 2-words or more first name separated by space
	elif re.match(r"(\w+ )+\w+$", first):
		first_spaced_multi_counter += 1

	# others
	else:
		first_other_counter += 1
		# print(last, first)

	first_counters = first_simple_counter, first_init_dot_counter, first_dash_counter, first_spaced_multi_counter, first_other_counter
		
	return first, first_counters


def populate_sna_ids():
	sna_ids = {}
	with open('All_Faculty.csv', 'r') as faculty:
		reader = csv.reader(faculty, delimiter=',')
		line = 0
		
		# there's 5 last name cases to be counted
		last_counters = (0 for _ in range(5))
		first_counters = (0 for _ in range(5))

		for row in reader:
			if line != 0:
				sna_id = row[1]
				last = row[3].strip().casefold()
				first = row[4].strip().casefold()
				last, last_counters = process_last_name(last, first, last_counters)
				first, first_counters = process_first_name(first, last, first_counters)
				full = ','.join([last,first])
				sna_ids[full] = sna_id
			line += 1

		print(f'\nprocessed {line-1} investigators\n')

		last_simple_counter, last_double_counter, last_parens_counter, last_spaced_multi_counter, last_other_counter = last_counters
		print(f'cases of 1-word last names: {last_simple_counter}')
		print(f'cases of 2-word last names: {last_double_counter}')
		print(f'cases of parentheses last names: {last_parens_counter}')
		print(f'cases of multiple words with spaces last names: {last_spaced_multi_counter}')
		print(f'cases of other last names: {last_other_counter}')

		first_simple_counter, first_init_dot_counter, first_dash_counter, first_spaced_multi_counter, first_other_counter = first_counters
		print(f'\ncases of 1-word first names: {first_simple_counter}')
		print(f'cases of initial dot 1-word first names: {first_init_dot_counter}')
		print(f'cases of 2-or-more-words-separated-by-dash first names: {first_dash_counter}')
		print(f'cases of multiple words with spaces first names: {first_spaced_multi_counter}')
		print(f'cases of other first names: {first_other_counter}')

	return sna_ids



def swap_names_sna_ids(sna_ids):
	with open('ALL FIXED Funding Data for Research SNA 08292018.csv', 'r') as data,\
		open('SNA ID ALL FIXED Funding Data for Research SNA 08292018.csv', 'w', newline='') as output,\
		open('couldnt_find_sna_id_for_these_ones.csv', 'w', newline='') as errors:
		reader = csv.reader(data, delimiter=',')
		writer = csv.writer(output, delimiter=',')
		err_writer = csv.writer(errors, delimiter=',')
		line = 0
		err_counter = 0
		insert_index = 14
		for row in reader:
			correct_row = row
			if line != 0:
				full = correct_row[insert_index-2]
				try:
					sna_id = sna_ids[full.strip().casefold()]
					last, first = full.split(',')
					data = (sna_id, last, first)
					for i in range(insert_index,insert_index+3):
						correct_row.insert(i,data[i-insert_index])
					writer.writerow(correct_row)
				except KeyError:
					# if error in obtaining sna then try removing the post fixed middle initial
					try:
						full_name_clean = full.split(',')
						first = full_name_clean[1].split()[0]
						full_name_clean = ','.join([full_name_clean[0], first])
						sna_id = sna_ids[full_name_clean.casefold()]
						last, first = full_name_clean.split(',')
						data = (sna_id, last, first)
						for i in range(insert_index,insert_index+3):
							correct_row.insert(i,data[i-insert_index])
						writer.writerow(correct_row)
					except KeyError:
						err_writer.writerow([full, full_name_clean])
						err_counter += 1
						last, first = full.split(',')
						data = ('', last, first)
						for i in range(insert_index,insert_index+3):
							correct_row.insert(i,data[i-insert_index])
						writer.writerow(correct_row)
					except IndexError:
						print('can\'t do', full, line)

			else:
				data = ('SNA ID', 'Last Name', 'First Name')
				for i in range(insert_index,insert_index+3):
					correct_row.insert(i,data[i-insert_index])
				writer.writerow(correct_row)
				err_writer.writerow(['Original Name', 'Name without 2nd part of First Name'])

			line += 1
		print(f'\nprocessed {line-1} lines of investigators')
		print(f'couldn\'t find {err_counter} SNA IDs')



def main():
	fix_names()
	sna_ids = populate_sna_ids()
	swap_names_sna_ids(sna_ids)


if __name__ == '__main__':
	main()