import json
import argparse

def process_notebook(notebook):
    result = ""

    for cell in notebook['cells']:
        if cell['cell_type'] == 'markdown':
            for line in cell['source']:
                result += line + "\n"
        elif cell['cell_type'] == 'code':
            result += '\n```python\n'
            for line in cell['source']:
                result += line + "\n"
            result += '```\n'
            result += "\nOutput:\n"
            for line in cell['outputs']:
                for k, v in line['data'].items():
                    if 'latex' in k:
                        for l in v:
                            result += "\n$$\n"
                            result += l[1:-1].replace(r'_', r'\_').replace(r'\\', r'\\\\') + "\n"
                            result += "$$\n"

    return result

def main():
    parser = argparse.ArgumentParser(description='Convert Jupyter notebook to Markdown.')
    parser.add_argument('input_file', type=str, help='Path to the input Jupyter notebook file.')

    args = parser.parse_args()

    with open(args.input_file, mode="r", encoding="utf-8") as f:
        notebook = json.load(f)

    output_file = args.input_file.replace('.ipynb', '.md')

    with open(output_file, 'w') as f:
        f.write(process_notebook(notebook))

if __name__ == "__main__":
    main()
