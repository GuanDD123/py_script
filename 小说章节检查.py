from pathlib import Path
from rich import print
from rich.table import Table
from rich.prompt import Prompt
from textwrap import dedent
from re import match
from typing import Literal

from _general import WHITE, YELLOW, GREEN, RED, CYAN, DELIMITER


class CheckFile:
    counts_warning = 2000
    lines_warning = 30
    chapter_pattern = r'^(第[\d零一二三四五六七八九十百千]+章)|(## .*?章) ?'

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath

    def run(self) -> Literal['q'] | None:
        self._check_chapter()
        self._show_result()
        return self._modify_file()

    def _check_chapter(self) -> None:
        with open(str(self.filepath), encoding='utf-8') as f:
            content_lines = f.readlines()

        self.content = []
        self.chapters = 0
        counts = 0
        lines = 0
        title = ''
        chapter_mark = ''
        self.infos = []
        for content_line in content_lines:
            if content_line.startswith('第') or content_line.startswith('##'):
                if chapter_mark_match := match(self.chapter_pattern, content_line):
                    if self.chapters:
                        self._deal_info(title.rstrip('\n'), chapter_mark, counts, lines)
                    title = content_line
                    chapter_mark = chapter_mark_match.group()
                    self.chapters += 1
                    counts = 0
                    lines = 0
                    self.content.append(content_line.replace(chapter_mark_match.group(), f'第{self.chapters}章 ', 1))
            elif content_line:
                counts += len(content_line.strip())
                lines += 1
                self.content.append(content_line)
        self._deal_info(title.rstrip('\n'), chapter_mark, counts, lines)

    def _modify_file(self) -> Literal['q'] | None:
        modify = Prompt.ask(f'[{CYAN}]是否修改', choices=['\n', 'n', 'q'])
        if modify == '\n':
            self.filepath.write_text(''.join(self.content), encoding='utf-8')
        elif modify == 'q':
            return 'q'

    def _deal_info(self, title: str, mark: str, counts: int, lines: int) -> None:
        self.infos.append((mark,
                           title.replace(mark, f'第{self.chapters}章 ', 1),
                           counts, lines))

    def _show_result(self) -> None:
        table = Table(title=str(self.filepath.stem), title_style=CYAN,
                      style=WHITE, show_lines=True, expand=True,
                      header_style=WHITE)

        table.add_column('Mark')
        table.add_column('New Title')
        table.add_column('Counts')
        table.add_column('Lines')

        if self.infos:
            for info in self.infos:
                mark, new_title, counts, lines = info
                if counts < self.counts_warning:
                    counts_color = YELLOW
                else:
                    counts_color = GREEN
                if lines < self.lines_warning:
                    lines_color = YELLOW
                else:
                    lines_color = GREEN
                table.add_row(mark, new_title, f'[{counts_color}]{counts}', f'[{lines_color}]{lines}')
            print(table)


class CheckDir():
    def __init__(self, dirpath: Path) -> None:
        self.dirpath = dirpath

    def run(self) -> None:
        try:
            for filepath in self.dirpath.iterdir():
                CheckFile(filepath).run()
                print(f'\n{"="*20}\n')
        except Exception as e:
            print(f'[{RED}]{e}')


if __name__ == '__main__':
    tips = dedent(
        f'''
        {DELIMITER}
        1. 检查文件夹中所有小说
        2. 检查某本小说
        {DELIMITER}

        请选择运行模式'''
    )

    mode = Prompt.ask(f'[{CYAN}]{tips}', choices=['q', '1', '2'])
    if mode != 'q':
        while True:
            path = Prompt.ask(f'\n[{CYAN}]请输入文件/文件夹路径').strip()
            if path.lower() == 'q':
                break
            elif not path:
                continue

            if mode == '1':
                if CheckDir(Path(path)).run() == 'q':
                    break
            elif mode == '2':
                if CheckFile(Path(path)).run() == 'q':
                    break
