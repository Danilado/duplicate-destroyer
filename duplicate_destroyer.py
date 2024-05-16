import os
from filecmp import cmpfiles
from itertools import combinations

# the to the directory which subdirectories should be checked
MAIN_PATH = "./"

# prefix of directories to be checked
# can be empty
DIR_PREFIX = "lab_"

# name of subdir in each subdirectory of the main path
# can be empty
SUBDIR_TO_CHECK = "func_tests/scripts"

# filenames to check
# does not support *
FILES_TO_CHECK = ["pos_case.sh", "neg_case.sh",
                  "func_tests.sh", "comparator.sh"]


def get_subdirs(dir_path: str) -> list[str]:
    return sorted(
        list(
            filter(
                lambda name: os.path.isdir(name)
                and name.startswith(DIR_PREFIX),
                map(
                    lambda filename: os.fsdecode(filename),
                    os.listdir(os.fsencode(dir_path))
                )
            )
        )
    )


def get_target_dirs(dirs: list[str]) -> list[str]:
    return list(
        filter(
            lambda dirname: os.path.isdir(dirname),
            map(
                lambda filename: MAIN_PATH +
                os.path.join(filename, SUBDIR_TO_CHECK),
                dirs
            )
        )
    )


def cmp_directories(dirs: list[str]) -> dict[str, str]:
    res: dict[str, str] = {}

    target_dirs = get_target_dirs(dirs)
    if len(target_dirs) == 0:
        raise ValueError("No matching directories")

    targets_to_check = [*combinations(target_dirs, 2)]
    i = 0
    while i < len(targets_to_check):
        dir1, dir2 = targets_to_check[i]

        matches, _, _ = cmpfiles(dir1, dir2, FILES_TO_CHECK)

        if len(matches) == len(FILES_TO_CHECK):
            res[dir2] = dir1
            targets_to_check = list(
                filter(
                    lambda fdirpair: dir2 not in fdirpair,
                    targets_to_check
                )
            )
        else:
            for match in matches:
                match1 = os.path.join(dir1, match)
                match2 = os.path.join(dir2, match)
                res[match2] = match1 if (match1) not in res.keys() \
                    else res[match1]
            i += 1

    return res


def unique(arr: list) -> list:
    return [x for i, x in enumerate(arr) if i == arr.index(x)]


def print_associations(assocs: dict[str, str]) -> None:
    print("associations: ")
    for val in unique(list(assocs.values())):
        print(f"files equal to {val}:" if not val.endswith(
            SUBDIR_TO_CHECK) else f"folders equal to {val}:")
        print(*sorted([key for key in assocs.keys()
              if assocs[key] == val]), sep="\n", end="\n\n")


def delete_file(filename: str) -> None:
    if os.path.isfile(filename) or os.path.islink(filename):
        os.unlink(filename)


def replace_file(filename1: str, filename2: str) -> None:
    try:
        delete_file(filename1)
        try:
            print(f"Creating link {filename2} -> {filename1}")
            os.symlink(os.path.relpath(
                filename2, os.path.dirname(filename1)), filename1)
        except Exception as e:
            print(f"Failed to create symbolic link for {filename1}. Reason: {e}\n",
                  "The file is lost, such a shame...")
    except Exception as e:
        print(f"Failed to delete {filename1}. Reason: {e}")


def replace_directory(path1: str, path2: str) -> None:
    for filename in FILES_TO_CHECK:
        replace_file(os.path.join(path1, filename),
                     os.path.join(path2, filename))


def replace_associations(assocs: dict[str, str]) -> None:
    for key in list(assocs.keys()):
        if key.endswith(SUBDIR_TO_CHECK):
            replace_directory(key, assocs[key])
        else:
            replace_file(key, assocs[key])


def main():
    subdirs = get_subdirs(MAIN_PATH)

    associations = cmp_directories(subdirs)
    print_associations(associations)

    conf = input(
        "Do you want to replace matching files with symbolic links?\n" +
        "ALL THE DUPLICATES WILL BE DELETED AND REPLACED WITH LINKS\n"
        "Type YES in caps, to proceed\n" +
        "> ")

    if conf == "YES":
        replace_associations(associations)
    else:
        print("Мудрое решение, хорошего дня")


if __name__ == "__main__":
    main()
