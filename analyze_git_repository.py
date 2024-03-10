from pathlib import Path
import sys

def main():
	def analyze(repository_path: str):
		"""
		Analyze a Git repository and make a text sting with the tree structure and each filname with file content.
		repository_path: Path of the repository.
		"""

		return make_tree(repository_path)[0], make_files(repository_path)

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

		file_data = {data.rstrip("\n") for data in file_data}

		file_data.add(".git/")
		file_data.add("package-lock.json")

		return file_data

	def make_tree(repository_path: str):
		"""
		Make a text string of the tree structure of the Git repository.
		repository_path: Path of the repository.
		"""

		repository_path = repository_path.rstrip("/")
		
		tree_path = Path(repository_path)
		tree = tree_path.name + '/'
		tree_dict = {}

		space =  '    '
		branch = '│   '

		tee =    '├── '
		last =   '└── '

		path_to_ignore = get_gitignore_data(repository_path + "/.gitignore")

		def make_tree_structure(dir_path: Path, prefix: str=''):
			contents = list(dir_path.iterdir())
			pointers = [tee] * (len(contents) - 1) + [last]
			for pointer, path in zip(pointers, contents):
				if path.is_dir() and (path.name + "/") in path_to_ignore:
					continue
				elif path.is_file() and path.name in path_to_ignore:
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
				if path.is_dir() and (path.name + "/") in path_to_ignore:
					continue
				elif path.is_file() and path.name in path_to_ignore:
					continue

				if path.is_dir():
					children[path.name + "/"] = make_tree_dict(path, path.name)
				else:
					children[path.name] = None

			return children

		tree_dict[tree_path.name] = make_tree_dict(tree_path)

		del make_tree_structure
		del make_tree_dict

		return tree, tree_dict

	def make_files(repository_path: str):
		"""
		Make a text string including files path and files content.
		repository_path: Path of the repository.
		"""

		repository_path = repository_path.rstrip("/")
		
		tree = make_tree(repository_path)[1]
		files = ''

		tree = list(tree.values())[0]

		def browse_tree(dic, current_path=''):
			nonlocal files
			for key, value in dic.items():
				if isinstance(value, dict):
					browse_tree(value, current_path + key + "/")
				else:
					content = open(repository_path + "/" + current_path + key, 'rb').read()

					try:
						content = content.decode('utf-8')
					except UnicodeDecodeError:
						content = "[Binary content cannot be displayed as text]"

					files = files + "`" + current_path + key + "`:\n"
					files = files + "```\n" + content + "\n```\n"
		
		browse_tree(tree)

		del browse_tree

		return files

	def make_context(repository_path: str):
		"""
		Create the text string context for the chabot.
		repository_path: Path of the repository.
		"""
		analized = analyze(repository_path)

		context = "We talk about the repository in the folder `" + repository_path + "`\nHere is the tree of the repository:\n" + analized[0] + "\nAnd here is all the files of the repository:\n" + analized[1]

		return context

	if len(sys.argv) >= 2:
		try:
			ctx = make_context(sys.argv[1])
			if len(sys.argv) >= 4:
				if sys.argv[2] == "-o" or sys.argv[2] == "--output":
					try:
						with open(sys.argv[3], 'w') as f:
							f.write(ctx)
					except FileNotFoundError as e:
						print(f'{e}\nTry to make yourself the directory before.')
				else:
					raise TypeError(f'Unknown parameter: {sys.argv[2]}')
			else:
				print(ctx)
		except Exception as e:
			print(str(e))

if __name__ == "__main__":
	main()