from pathlib import Path

from sage.all import *


def parse_kissat_file(kissat_file: Path, n: int) -> bool:
    result = None
    graph = ""

    with open(str(kissat_file), "r") as opened_file:
        for line in opened_file:
            line = line.strip()

            if line[0] == "s":
                if line == "s UNSATISFIABLE":
                    return False
                elif line == "s SATISFIABLE":
                    result = True
                else:
                    raise Error

            elif line[0] == "v":
                graph += line[1:]

    if result is None:
        return None

    split_graph = graph.split()
    g = Graph(n)
    counter = 0

    for i in range(n - 1):
        for j in range(i + 1, n):
            if "-" not in split_graph[counter]:
                g.add_edge(i, j)

            counter += 1

    assert split_graph[counter] == "0"

    output_path = Path("parsed_graphs") / kissat_file.relative_to(kissat_file.parts[0])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path = output_path.with_suffix(".g6")

    with open(str(output_path), "w") as opened_file:
        opened_file.write(g.graph6_string())

    return result


def parse_problem_folder(problem_folder: Path):
    solutions = {}

    min_a = float("inf")
    max_a = float("-inf")
    min_b = float("inf")
    max_b = float("-inf")

    for kissat_file in problem_folder.iterdir():
        if kissat_file.is_dir():
            continue
        if "_ord" not in kissat_file.name and "_cyc" not in kissat_file.name:
            continue

        split_stem = kissat_file.stem.split("_")

        a = int(split_stem[0][-2:])
        min_a = min(min_a, a)
        max_a = max(max_a, a)

        b = int(split_stem[1][-2:])
        min_b = min(min_b, b)
        max_b = max(max_b, b)

        n = int(split_stem[3])
        result = parse_kissat_file(kissat_file, n)

        if result is None:
            kissat_file.unlink()
            continue

        if (a, b) not in solutions:
            solutions[(a, b)] = [max(a, b), float("inf")]

        if result:
            solutions[(a, b)][0] = max(solutions[(a, b)][0], n + 1)
        else:
            solutions[(a, b)][1] = min(solutions[(a, b)][1], n)

    for kissat_file in problem_folder.iterdir():
        if kissat_file.is_dir():
            continue
        if "_ord" not in kissat_file.name and "_cyc" not in kissat_file.name:
            continue

        split_stem = kissat_file.stem.split("_")

        a = int(split_stem[0][-2:])
        b = int(split_stem[1][-2:])
        n = int(split_stem[3])
        result = parse_kissat_file(kissat_file, n)

        if result:
            if solutions[(a, b)][0] > n + 1:
                kissat_file.unlink()
                output_path = Path("parsed_graphs") / kissat_file.relative_to(kissat_file.parts[0])
                output_path = output_path.with_suffix(".g6")
                output_path.unlink()
        else:
            if solutions[(a, b)][1] < n:
                kissat_file.unlink()
                output_path = Path("parsed_graphs") / kissat_file.relative_to(kissat_file.parts[0])
                output_path = output_path.with_suffix(".g6")
                output_path.unlink()

    if max_a < 0:
        return

    output_path = Path("generated_tables") / f"{problem_folder.name}.tex"
    with open(str(output_path), "w") as opened_file:
        opened_file.write(r"\begin{table}[H]" + "\n")
        opened_file.write(r"\centering" + "\n")
        opened_file.write(r"\footnotesize" + "\n")
        r_string = "r" * (max_b - min_b + 1)
        opened_file.write(r"\begin{tabular}{|c||" + r_string + r"|}" + "\n")
        opened_file.write(r"\hline" + "\n")

        opened_file.write(r"\backslashbox{$a$}{$b$}")
        for b in range(min_b, max_b + 1):
            opened_file.write(f" & ${b}$")
        opened_file.write(r"\\" + "\n")
        opened_file.write(r"\hline" + "\n")
        opened_file.write(r"\hline" + "\n")

        for a in range(min_a, max_a + 1):
            opened_file.write(f"${a}$")

            for b in range(min_b, max_b + 1):
                if (a, b) not in solutions:
                    opened_file.write(" &")
                else:
                    sol = solutions[(a, b)]

                    if sol[0] == sol[1]:
                        opened_file.write(f" & ${sol[0]}$")
                    else:
                        assert sol[1] == float("inf")
                        opened_file.write(r" & $\ge " + f"{sol[0]}$")

            opened_file.write(r"\\" + "\n")

        opened_file.write(r"\hline" + "\n")
        opened_file.write(r"\end{tabular}" + "\n")
        opened_file.write(r"\label{" + f"{problem_folder.name}_tab" + "}\n")
        opened_file.write(r"\end{table}" + "\n")


def main():
    root = Path("kissat_output")

    for problem_folder in root.iterdir():
        if not problem_folder.is_dir():
            continue
        if "_ord" not in problem_folder.name and "_cyc" not in problem_folder.name:
            continue

        parse_problem_folder(problem_folder)


if __name__ == "__main__":
    main()
