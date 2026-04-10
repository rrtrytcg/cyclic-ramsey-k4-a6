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
                    result = False
                elif line == "s SATISFIABLE":
                    result = True
                else:
                    raise Error

            elif line[0] == "v":
                graph += line[1:]

    assert result is not None

    if result:
        split_graph = graph.split()
        g = Graph(n)
        counter = 0

        for i in range(n - 1):
            for j in range(i + 1, n):
                if "-" not in split_graph[counter]:
                    g.add_edge(i, j)
                
                counter +=1

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
        if problem_folder.name == "pqmon_pqmon" and "_cyc" in kissat_file.name:
            continue

        split_stem = kissat_file.stem.split("_")

        a = int(split_stem[0][-2:])
        min_a = min(min_a, a)
        max_a = max(max_a, a)

        b = int(split_stem[1][-2:])
        min_b = min(min_b, b)
        max_b = max(max_b, b)

        if (a, b) not in solutions:
            solutions[(a, b)] = [float("-inf"), float("inf")]

        n = int(split_stem[3])
        result = parse_kissat_file(kissat_file, n)

        if result:
            solutions[(a, b)][0] = max(solutions[(a, b)][0], n + 1)
        else:
            solutions[(a, b)][1] = min(solutions[(a, b)][1], n)

    for kissat_file in problem_folder.iterdir():
        if kissat_file.is_dir():
            continue
        if "_ord" not in kissat_file.name and "_cyc" not in kissat_file.name:
            continue
        if problem_folder.name == "pqmon_pqmon" and "_cyc" in kissat_file.name:
            continue

        split_stem = kissat_file.stem.split("_")

        a = int(split_stem[0][-2:])
        b = int(split_stem[1][-2:])
        n = int(split_stem[3])
        result = parse_kissat_file(kissat_file, n)

        if result:
            if solutions[(a, b)][0] > n + 1:
                kissat_file.unlink()
        else:
            if solutions[(a, b)][1] < n:
                kissat_file.unlink()

    output_path = Path("parsed_tables") / f"{problem_folder.name}.tex"
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
                    assert sol[0] >= 1

                    if sol[0] == sol[1]:
                        opened_file.write(f" & ${sol[0]}$")
                    else:
                        assert sol[1] == float("inf")
                        opened_file.write(r"& $\ge " + f"{sol[0]}$")

            opened_file.write(r"\\" + "\n")
        
        opened_file.write(r"\hline" + "\n")
        opened_file.write(r"\end{tabular}" + "\n")
        opened_file.write(r"\label{" + f"{problem_folder.name}_tab" + "}\n")
        opened_file.write(r"\end{table}" + "\n")

# \begin{table}[H]
# \centering
# \footnotesize
# \begin{tabular}{|c||rrrrrrrrrrrrrrrrrrrr|}
# \hline 
# \backslashbox{$a$}{$b$} & $3$ & $4$ & $5$ & $6$ & $7$ & $8$ & $9$ & $10$ & $11$ & $12$ & $13$ & $14$ & $15$ & $16$ & $17$ & $18$ & $19$ & $20$ & $21$ & $22$\\
# \hline
# \hline
# $3$ & $3$ & $4$ & $5$ & $6$ & $7$ & $8$ & $9$ & $10$ & $12$ & $12$ & $13$ & $14$ & $16$ & $17$ & $17$ & $18$ & $20$ & $21$ & $22$ & $22$\\
# $4$ & & $5$ & $6$ & $7$ & $9$ & $10$ & $10$ & $11$ & $12$ & $13$ & $14$ & $15$ & $16$ & $17$ & $18$ & $19$ & $20$ & $21$ & & \\
# $5$ & & & $8$ & $9$ & $10$ & $10$ & $11$ & $12$ & $13$ & $15$ & $16$ & $17$ & $17$ & $19$ & $20$ & $21$ & $22$ & & &\\
# $6$ & & & & $10$ & $11$ & $12$ & $13$ & $14$ & $14$ & $15$ & $17$ & $17$ & & & & & & & &\\
# $7$ & & & & & $12$ & $13$ & $13$ & $14$ & $16$ & $17$ & $17$ & & & & & & & & &\\
# $8$ & & & & & & $14$ & $15$ & $16$ & $17$ & $18$ & & & & & & & & & &\\
# \hline
# \end{tabular}
# \caption{Cyclic Ramsey numbers $R_\mathrm{cyc}(P_a^\mathrm{alt}, P_b^\mathrm{alt})$ with $3 \le a \le b$, $a \le 8$ and $b \le 22$.}
# \label{palt_palt_cyc_tab}
# \end{table}


def main():
    root = Path("kissat_output")

    for problem_folder in root.iterdir():
        if not problem_folder.is_dir():
            continue
        if (
            "_ord" not in problem_folder.name
            and "_cyc" not in problem_folder.name
            and "pqmon" not in problem_folder.name
        ):
            continue

        parse_problem_folder(problem_folder)


if __name__ == "__main__":
    main()
