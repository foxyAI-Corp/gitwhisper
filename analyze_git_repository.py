from pathlib import Path
import colorama
import inspect
import traceback
import argparse

def analyze(repository_path: str, gitignore_path: str = None):
	"""
	Analyze a Git repository and make a text sting with the tree structure and each filname with file content.
	repository_path: Path of the repository.
	"""
	if gitignore_path != None and type(gitignore_path) == str:
		tree = make_tree(repository_path, gitignore_path=gitignore_path)[0]
	else:
		tree = make_tree(repository_path)[0]

	if gitignore_path != None and type(gitignore_path) == str:
		files = make_files(repository_path, gitignore_path=gitignore_path)
	else:
		files = make_files(repository_path)

	return tree, files

def get_gitignore_data(gitignore_file_path: str):
	"""
	Get the data from the `.gitignore` file.
	gitignore_file_path: Path of the `.gitignore` file.
	"""

	try:
		with open(gitignore_file_path, "r") as f:
			file_data = set(f.readlines())
	except FileNotFoundError:
		file_data = set([])

	file_data = {data.rstrip() for data in file_data}

	file_data.add(".git/")
	file_data.add("package-lock.json")
	file_data.add("node_modules/")
	file_data.add("LICENSE")

	return file_data

def make_tree(repository_path: str, gitignore_path: str = None):
	"""
	Make a text string of the tree structure of the Git repository.
	repository_path: Path of the repository.
	"""

	repository_path = repository_path.rstrip("/")
	
	tree_path = Path(repository_path).absolute()
	tree = tree_path.name + '/'
	tree_dict = {}

	space =  ' ' * 4
	branch = '│   '

	tee =    '├── '
	last =   '└── '

	if gitignore_path != None and type(gitignore_path) == str:
		path_to_ignore = get_gitignore_data(gitignore_path)
	else:
		path_to_ignore = get_gitignore_data(repository_path + "/.gitignore")

	def make_tree_structure(dir_path: Path, prefix: str=''):
		contents = list(dir_path.iterdir())
		pointers = [tee] * (len(contents) - 1) + [last]
		for pointer, path in zip(pointers, contents):
			path_name = path.name.rstrip("/")
			path_name = path_name.lstrip("/")
			path_dir = str(path.relative_to(Path(repository_path).absolute())).rstrip("/").replace('\\', '/').lstrip("/")

			for p in path_to_ignore:
				if len(p) >= 1:
					if p[-1] == "/":
						if path.is_file():
							if path_dir.startswith(p):
								continue

			if path.is_dir() and (path_dir + "/") in path_to_ignore:
				continue
			elif path.is_file() and path_dir in path_to_ignore:
				continue
			if path.is_dir():
				yield prefix + pointer + path.name + "/"
				extension = branch if pointer == tee else space
				yield from make_tree_structure(path, prefix=prefix+extension)
			else:
				yield prefix + pointer + path.name
	
	for line in make_tree_structure(tree_path):
		tree = tree + "\n" + line

	def make_tree_dict(dir_path: Path, parent_key=None):
		contents = list(dir_path.iterdir())
		children = {}

		for path in contents:
			path_name = path.name.rstrip("/")
			path_name = path_name.lstrip("/")
			path_dir = str(path.relative_to(Path(repository_path).absolute())).replace('\\', '/').rstrip("/").lstrip("/")

			for p in path_to_ignore:
				if len(p) >= 1:
					if p[-1] == "/":
						if path.is_file():
							if path_dir.startswith(p):
								continue


			if path.is_dir() and (path_dir + "/") in path_to_ignore:
				continue
			elif path.is_file() and path_dir in path_to_ignore:
				continue
			elif path.is_dir():
				children[path_name + "/"] = make_tree_dict(path, path_name)
			else:
				children[path_name] = None

		return children

	tree_dict[tree_path.name] = make_tree_dict(tree_path)

	del make_tree_structure
	del make_tree_dict

	return tree, tree_dict

def make_files(repository_path: str, gitignore_path: str = None):
	"""
	Make a text string including files path and files content.
	repository_path: Path of the repository.
	"""

	repository_path = repository_path.rstrip("/")
	
	if gitignore_path != None and type(gitignore_path) == str:
		tree = make_tree(repository_path, gitignore_path=gitignore_path)[1]
	else:
		tree = make_tree(repository_path)[1]
	files = ''

	tree = list(tree.values())[0]

	def browse_tree(dic, current_path=''):
		nonlocal files
		for key, value in dic.items():
			if isinstance(value, dict):
				browse_tree(value, current_path + key)
			else:
				content = open(repository_path + "/" + current_path + key, 'rb').read()

				try:
					content = content.decode('utf-8')
				except UnicodeDecodeError:
					content = "[Binary content cannot be displayed as text]"
				
				content = content.replace("\t", " " * 4)

				files = files + "`" + current_path + key + "`:\n"
				files = files + "```\n" + content + "\n```\n"
	
	browse_tree(tree)

	del browse_tree

	return files

def make_context(repository_path: str, gitignore_path: str = None):
	"""
	Create the text string context for the chabot.
	repository_path: Path of the repository.
	"""
	if gitignore_path != None and type(gitignore_path) == str:
		analized = analyze(repository_path, gitignore_path=gitignore_path)
	else:
		analized = analyze(repository_path)

	context = "We talk about the repository in the folder `" + str(Path(repository_path).absolute()).replace("\\", "/") + "`\nHere is the tree of the repository:\n" + analized[0] + "\nAnd here is all the files of the repository:\n" + analized[1]

	return context

def main():
	parser = argparse.ArgumentParser(description="Analyze a Git repository and provide its tree structure and file contents.")
	parser.add_argument("repository_path", help="Path of the Git repository.")
	parser.add_argument("--output", "-o", metavar="output_file", help="Output file to save the analysis.")
	parser.add_argument("--gitignore", "-g", metavar="gitignore_file", help="Path to a custom `.gitignore` file.")

	colorama.init(convert=True)

	args, unknown_args = parser.parse_known_args()

	try:
		if not args.gitignore:
			ctx = make_context(args.repository_path)
		else:
			if Path(args.gitignore).is_file():
				ctx = make_context(args.repository_path, gitignore_path=args.gitignore)
			else:
				raise FileNotFoundError(f'No such file: "{args.gitignore}"')

		if args.output:
			output_dir = Path(args.output).parent
			if not output_dir.is_dir():
				output_dir.mkdir(parents=True)
			with open(args.output, 'w', encoding='utf-8') as f:
				f.write(ctx)
		else:
			print(ctx)
		
		if unknown_args:
			for arg in unknown_args:
				raise TypeError(f'Unknown parameter: "{arg}"')
	except Exception as e:
		tb_info = traceback.extract_tb(e.__traceback__)
		_, line_num, func_name, _ = tb_info[-1]
		error = str(e)
		error = error[0].upper() + error[1:]

		obj = globals().get(func_name)
		if inspect.isfunction(obj):
			func_name += "()"

		print(f'{colorama.Fore.RED}Error ({type(e).__name__}):')
		print(f'    Line {line_num} in {func_name}: {error}{colorama.Fore.RESET}')

if __name__ == "__main__":
	main()