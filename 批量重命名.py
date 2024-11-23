from pathlib import Path
from random import randint
from string import ascii_lowercase, digits
from rich import print
from rich.prompt import Prompt
from re import compile, sub, Pattern
from rich.table import Table
from textwrap import dedent

from _general import WHITE,  GREEN, RED, CYAN, DELIMITER


class RenameRandom:
    base_str = ascii_lowercase + digits

    def __init__(self, dirpath: Path, name_length: int) -> None:
        self.dirpath = dirpath
        self.name_length = name_length

    def run(self) -> None:
        try:
            for path in self.dirpath.iterdir():
                if path.is_dir():
                    self._rename_dir(path)
                else:
                    self._rename_file(path)
        except Exception as e:
            print(f'[{RED}]{e}')

    def _rename_dir(self, dirpath_child: Path) -> None:
        new_dirname, new_dirpath = self._generate_name_path(dirpath_child)
        dirpath_child.rename(new_dirpath)
        for num, filepath in enumerate(new_dirpath.iterdir(), start=1):
            filepath.rename(new_dirpath.joinpath(f'{new_dirname} ({num}) {filepath.suffix}'))
        print(f'[{GREEN}]{dirpath_child} 重命名完毕')

    def _rename_file(self, filepath: Path) -> None:
        _, new_filepath = self._generate_name_path(filepath)
        filepath.rename(new_filepath)
        print(f'[{GREEN}]{filepath} 重命名完毕')

    def _generate_name_path(self, path: Path) -> tuple[str, Path]:
        base_str_length = len(self.base_str)
        new_name = ''.join(self.base_str[randint(0, base_str_length-1)] for _ in range(self.name_length))
        new_path = path.with_name(new_name+path.suffix)
        if not new_path.exists():
            return (new_name, new_path)
        else:
            self._generate_name_path()


class RenameDouYin:
    patterns = (
        (compile(r'^.*-视频-'), ''),
        (compile(r' *#无任何不良引导'), ''),
        (compile(r' *(回复 *)?@.*? (?!\()'), ''),
        (compile(r' *(回复 *)?@.*'), ''),
        (compile(r'^ *#.*? (?!\()'), ''),
        (compile(r'^ *#'), ''),
        (compile(r' *#.*'), '')
    )

    def __init__(self, dirpath: Path, name_length: int = None) -> None:
        self.dirpath = dirpath

    def run(self) -> None:
        index = 0
        while index < len(self.patterns):
            filepaths = []
            filename_set = {filepath.stem for filepath in self.dirpath.iterdir()}
            pattern, replace = self.patterns[index]
            try:
                for filepath in self.dirpath.iterdir():
                    new_filename, new_filepath = self._generate_name_path(filepath, pattern, replace, filename_set)
                    if (new_filename):
                        filename_set.add(new_filename)
                        filepaths.append((filepath, new_filepath))
            except Exception as e:
                print(f'[{RED}]{e}')
                return
            self._show_result(filepaths, pattern)
            if filepaths:
                if Prompt.ask(f'[{CYAN}]是否重命名', choices=['\n', 'n']) == '\n':
                    for filepath in filepaths:
                        old_filepath, new_filepath = filepath
                        old_filepath.rename(new_filepath)
                else:
                    return
            else:
                index += 1
        self.dirpath.rename(self.dirpath.with_name(sub(r'UID\d+_', '', self.dirpath.stem)))

    @staticmethod
    def _generate_name_path(filepath: Path, pattern: Pattern, replace: str, filename_set: set) -> tuple[str, Path]:
        old_filename, filetype = filepath.stem, filepath.suffix
        new_filename = sub(pattern, replace, old_filename)
        if old_filename != new_filename:
            if new_filename in filename_set:
                new_filename = sub(r' \(\d+\)$', '', new_filename)
                while (new_filename := f'{new_filename} ({randint(1, 99999)})') in filename_set:
                    continue
            return (new_filename, filepath.with_name(new_filename+filetype))
        else:
            return (None, None)

    def _show_result(self, filepaths: list[tuple[Path, Path]], pattern: Pattern) -> None:
        table = Table(title=f'\n使用正则表达式 {pattern} 重命名', title_style=CYAN,
                      style=WHITE, show_lines=True, expand=True,
                      header_style=WHITE)

        table.add_column('原文件名')
        table.add_column('新文件名')

        if filepaths:
            for filepath in filepaths:
                old_filepath, new_filepath = filepath
                table.add_row(f'[{CYAN}]{old_filepath.name}', f'[{GREEN}]{new_filepath.name}')
            print(table)


if __name__ == '__main__':
    tips = dedent(
        f'''
        {DELIMITER}
        1. 随机命名为 9 位字符串
        2. 随机命名为 15 位字符串
        {DELIMITER}
        3. 抖音视频重命名
        4. 抖音多文件夹视频重命名
        {DELIMITER}

        请选择运行模式'''
    )

    mode = Prompt.ask(f'[{CYAN}]{tips}', choices=['q', '1', '2', '3', '4'])
    if mode != 'q':
        while True:
            dirpath_str = Prompt.ask(f'\n[{CYAN}]请输入文件夹路径').strip()
            if dirpath_str.lower() == 'q':
                break
            elif not dirpath_str:
                continue
            dirpath = Path(dirpath_str)

            if mode == '1':
                RenameRandom(dirpath, 9).run()
            elif mode == '2':
                RenameRandom(dirpath, 15).run()
            elif mode == '3':
                RenameDouYin(dirpath).run()
            elif mode == '4':
                for dirpath_child in dirpath.iterdir():
                    if dirpath_child.stem.startswith('UID'):
                        if Prompt.ask(f'\n[{CYAN}]{dirpath_child.name}重命名？', choices=['\n', 'n']) == '\n':
                            RenameDouYin(dirpath_child).run()
