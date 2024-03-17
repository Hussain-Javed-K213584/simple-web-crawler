#!/usr/bin/python3
import requests
import re
from bs4 import BeautifulSoup
import click
from random import randint
from tabulate import tabulate

def get_html_of(url: str) -> str:
	"""
		Provide a URL to recieve the HTML code of the webpage.
		
		Parameters
		----------
		url: str
			The URL string to get the HTML code of
		Returns
		-------
		str
			The decoded HTML code in string format
	"""
	resp = requests.get(url)

	if resp.status_code != 200:
		print(f"HTTP status code of {resp.status_code} returned, expected 200...Exiting.")
		exit(1)

	return resp.content.decode()

def count_occurrences_in(word_list: list, min_length: int) -> dict:
	"""
	The function counts the occurence of words in the html code and returns a dictionary.

	Parameters
	----------
		word_list: list
			the word list created after crawling the web page.
		min_length: int
			the minimum length acceptable for a word to be added
	Returns
	-------
	dict
		Returns a dictionary of {word: str, occurence: int}
	"""
	word_count = {}

	for word in word_list:
		if len(word) < min_length:
			continue
		if word not in word_count:
			word_count[word] = 1
		else:
			current_count = word_count.get(word)
			word_count[word] = current_count + 1
	return word_count

def get_all_words_from(url: str) -> list:
	"""
	Grabs the HTML code of a website and parses it to get the words.
	Ignores HTML tags.

	Parameters
	---
	url: str
		a url string of the webpage to crawl.
	
	Returns
	-------
	list
		a list of words fetched from the webpage.
	"""
	html = get_html_of(url)
	soup = BeautifulSoup(html, 'html.parser')
	raw_text = soup.get_text()
	return re.findall(r'\w+', raw_text)

def get_top_words_from(all_words, length) -> list:
	"""
	Counts the occurences of words that were found in the webpage.

	Parameters
	----------
	all_words: list
		a list of words that were fetched from the webpage
	length: int
		the minimum length acceptable for a word to be added
	"""
	occurences = count_occurrences_in(all_words, length)
	return sorted(occurences.items(), key=lambda item: item[1], reverse=True)

def apply_password_mutation(word_list: list) -> list:
	"""Convert word list to common passwords"""
	numerics = [x for x in range(10)]
	from string import punctuation
	words = [word[0] for word in word_list] # Convert tuple into list of words
	passwd_list = []
	for word in words:
		word[0].upper()
		for i in range(4):
			word = word + str(randint(0, 9))
		word = word + punctuation[randint(0, len(punctuation) - 1)]
		passwd_list.append(word)
	del words
	return passwd_list

def convert_to_table(words: list) -> list:
	"""Provide a 1D list to convert to 2D list"""
	table = []
	for word in words:
		table.append([word])
	return table

@click.command()
@click.option('--url', '-u', prompt='Web Url', help='URL of webpage to extract from.')
@click.option('--length', '-l', default=0, help='Minimum word length (default: 0, no limit).')
@click.option('--output', '-o', default='', help="Save the output to a file.")
@click.option('--passwd', '-p', is_flag=True, help='Add common password mutation to the words fetched.')
def main(url, length, output, passwd):
	the_words = get_all_words_from(url)
	top_words = get_top_words_from(the_words, length)
	words = [word[0] for word in top_words]
	table = tabulate(convert_to_table(words), headers=['Top Words'], tablefmt='fancy_grid')
	if output != '':
		output_file = open(output, 'w')
		try:
			output_file.write(table)
			output_file.write('\n')
		finally:
			output_file.close()
	else:
		print(table)
	if passwd:
		passwd_list = apply_password_mutation(top_words)
		passwd_table = tabulate(convert_to_table(passwd_list), headers=['Possible Passwords'], tablefmt='fancy_grid')
		if output != '':
			try:
				output_file = open(output, 'a')
				output_file.write('Password Mutations:\n')
				output_file.write(passwd_table)
				output_file.write('\n')
			finally:
				output_file.close()
		else:
			print("Possible Passwords:")
			print(passwd_table)
	

if __name__ == '__main__':
	main()