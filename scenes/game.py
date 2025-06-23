import pygame
from base import SceneBase
import json
import os

from utils.button import draw_button

class GameScene(SceneBase):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.width, self.height = self.screen.get_size()
        self.font = pygame.font.Font("assets/LightNovel.otf", 29)
        self.bg_color = (50, 50, 80)
        self.bg_image = None  # 現在の背景画像
        self.chara_image = None  # 現在の立ち絵
        self.chara_info = None  # (kind, face_num)
        self.bg_map = {
            "1": "BG/Home.png",
            "2": "BG/Forest.png",
            "3": "BG/DemonKing.png",
            "4": "BG/BadEnd.png",
            "5": "BG/DustDemonKing.png",
            "6": "BG/TrueEnd.png",
            # 必要に応じて他の背景も追加可能
        }

        # シナリオデータの読み込み
        scenario_path = os.path.join("scenarios", "episode1.json")
        try:
            with open(scenario_path, encoding="utf-8") as f:
                self.scenario = json.load(f)
        except Exception as e:
            self.scenario = {"0,0": ["0￥エラー$シナリオが読み込めませんでした。$改行"]}

        # 最初のチャプター
        self.chapters = list(self.scenario.keys())
        self.chapter = self.chapters[0] if self.chapters else None
        self.line_index = 0
        self.lines = self.scenario.get(self.chapter, [])
        self.history = []  # 表示履歴
        self.max_history = 7
        self.name_map = {"0": "", "1": "リオ", "2": "師匠", "3": "魔王", "4": "???"}
        # 名前ごとの色マップ
        self.name_color_map = {
            "": (255, 255, 255),
            "リオ": (255, 200, 100),
            "師匠": (100, 200, 255),
            "魔王": (255, 100, 100),
            "???": (180, 180, 255),
        }

        self.text_window_rect = pygame.Rect(100, self.height - 350, self.width - 200, 300)
        self.back_btn = pygame.Rect(50, 50, 150, 50)

        # 追加: 選択肢表示フラグとボタン、選択肢リスト
        self.show_choices = False
        self.choice_buttons = []
        self.choices = []

        self.text_display_index = 0  # 1行の何文字目まで表示するか
        self.text_display_speed = 1  # 1フレームで何文字進めるか
        self.is_text_animating = False  # テキストアニメ中か
        self.last_text = None  # 現在アニメ中のテキスト

        # クリック音のロード
        self.click_sound = None
        try:
            self.click_sound = pygame.mixer.Sound(os.path.join("assets", "click.mp3"))
        except Exception:
            self.click_sound = None

    def decode_scenario_line(self, line):
        # choicesコマンド（分岐情報）をdictで受け取る
        if isinstance(line, dict) and "choices" in line:
            return [line]
        # 背景切り替え命令（番号対応）
        if line.startswith("bg="):
            bg_id = line[3:].strip()
            return [{"bg": bg_id}]
        # 立ち絵切り替え命令（例: cha=girl,1,2 または cha=none）
        if line.startswith("cha="):
            try:
                _, params = line.split("=", 1)
                params = [x.strip() for x in params.split(",")]
                # 立ち絵を消す命令
                if params[0].lower() == "none":
                    return [{"cha": ("none",)}]
                if len(params) == 3:
                    kind, face_num, pos_num = params
                elif len(params) == 2:
                    kind, face_num = params
                    pos_num = "1"  # デフォルト位置
                elif len(params) == 1:
                    kind = params[0]
                    face_num = "1"
                    pos_num = "1"
                else:
                    return []
                return [{"cha": (kind, face_num, pos_num)}]
            except Exception:
                return []
        # 例: "2よし、公園で食べちゃお。$覚めるともったいないし。"
        if not line:
            return []
        
        #１終了フラグ
        if line == "end":
            return [{"end": True}]
        
        name_num = line[0]
        text = line[1:]
        name = self.name_map.get(name_num, "")
        # $で分割して複数行対応。2行目以降は名前なし
        lines = text.split("$")
        result = []
        for idx, l in enumerate(lines):
            l = l.strip()
            if l:
                if idx == 0:
                    result.append({"name": name, "text": l})
                else:
                    result.append({"name": "", "text": l})
        return result

    def jump_to_chapter(self, chapter_key):
        # 分岐先のチャプターにジャンプ
        if chapter_key in self.scenario:
            self.chapter = chapter_key
            self.lines = self.scenario[chapter_key]
            self.line_index = 0
            self.history = []
            self.chara_image = None
            self.chara_info = None
            # チャプター開始時にbg/cha命令をすべて即時適用し、最初のテキスト行からクリックで進む
            while self.line_index < len(self.lines):
                parsed_lines = self.decode_scenario_line(self.lines[self.line_index])
                if len(parsed_lines) == 1 and ("bg" in parsed_lines[0] or "cha" in parsed_lines[0]):
                    if "bg" in parsed_lines[0]:
                        bg_id = parsed_lines[0]["bg"]
                        bg_file = self.bg_map.get(bg_id)
                        if bg_file:
                            bg_path = os.path.join("assets", bg_file)
                            if os.path.exists(bg_path):
                                self.bg_image = pygame.image.load(bg_path)
                    elif "cha" in parsed_lines[0]:
                        cha_info = parsed_lines[0]["cha"]
                        if cha_info[0] == "none":
                            self.chara_image = None
                            self.chara_info = None
                        else:
                            kind = cha_info[0]
                            face_num = cha_info[1] if len(cha_info) > 1 else "1"
                            pos_num = cha_info[2] if len(cha_info) > 2 else "1"
                            img_path = os.path.join("assets", "Cha", kind, f"{face_num}.png")
                            if os.path.exists(img_path):
                                self.chara_image = pygame.image.load(img_path)
                                self.chara_info = (kind, face_num, pos_num)
                            else:
                                self.chara_image = None
                                self.chara_info = None
                    self.line_index += 1
                else:
                    break

    def process_input(self, events, keys):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.back_btn.collidepoint(event.pos):
                    from scenes.title import HomeScene
                    self.switch_to_scene(HomeScene())
                elif self.show_choices:
                    for idx, btn in enumerate(self.choice_buttons):
                        if btn.collidepoint(event.pos):
                            if 0 <= idx < len(self.choices):
                                jump_key = self.choices[idx]["jump"]
                                self.jump_to_chapter(jump_key)
                                self.show_choices = False
                                return
                elif self.text_window_rect.collidepoint(event.pos):
                    # クリック音を再生
                    if self.click_sound:
                        self.click_sound.play()
                    # テキストアニメ中なら全文即表示、全文表示済みなら次へ
                    if self.is_text_animating:
                        self.text_display_index = len(self.last_text)
                        self.is_text_animating = False
                        return
                    # bg/cha/choices以外のテキストのみクリックで進める
                    while self.line_index < len(self.lines):
                        parsed_lines = self.decode_scenario_line(self.lines[self.line_index])
                        
                        if len(parsed_lines) == 1 and "end" in parsed_lines[0]:
                            from scenes.title import HomeScene
                            self.switch_to_scene(HomeScene())
                            return
                        
                        if len(parsed_lines) == 1 and isinstance(parsed_lines[0], dict) and "choices" in parsed_lines[0]:
                            self.choices = parsed_lines[0]["choices"]
                            self.show_choices = True
                            self.line_index += 1
                            return
                        if len(parsed_lines) == 1 and ("bg" in parsed_lines[0] or "cha" in parsed_lines[0]):
                            # bg/cha命令はスキップ（jump_to_chapterで既に適用済み or 途中で出てきた場合も即時適用してスキップ）
                            if "bg" in parsed_lines[0]:
                                bg_id = parsed_lines[0]["bg"]
                                bg_file = self.bg_map.get(bg_id)
                                if bg_file:
                                    bg_path = os.path.join("assets", bg_file)
                                    if os.path.exists(bg_path):
                                        self.bg_image = pygame.image.load(bg_path)
                            elif "cha" in parsed_lines[0]:
                                cha_info = parsed_lines[0]["cha"]
                                if cha_info[0] == "none":
                                    self.chara_image = None
                                    self.chara_info = None
                                else:
                                    kind = cha_info[0]
                                    face_num = cha_info[1] if len(cha_info) > 1 else "1"
                                    pos_num = cha_info[2] if len(cha_info) > 2 else "1"
                                    img_path = os.path.join("assets", "Cha", kind, f"{face_num}.png")
                                    if os.path.exists(img_path):
                                        self.chara_image = pygame.image.load(img_path)
                                        self.chara_info = (kind, face_num, pos_num)
                                    else:
                                        self.chara_image = None
                                        self.chara_info = None
                            self.line_index += 1
                            continue
                        else:
                            # テキストアニメ開始
                            self.history = []
                            self.history.extend(parsed_lines)
                            if self.history:
                                self.text_display_index = 0
                                self.is_text_animating = True
                                self.last_text = self.history[-1]["text"]
                            self.line_index += 1
                            return

    def update(self):
        # テキストアニメーション進行
        if self.is_text_animating and self.last_text is not None:
            self.text_display_index += self.text_display_speed
            if self.text_display_index >= len(self.last_text):
                self.text_display_index = len(self.last_text)
                self.is_text_animating = False

    def render(self, screen):
        # 背景描画
        if self.bg_image:
            screen.blit(pygame.transform.scale(self.bg_image, (self.width, self.height)), (0, 0))
        else:
            screen.fill(self.bg_color)
        # 立ち絵描画（位置・拡大率プリセット対応）
        if self.chara_image and self.chara_info:
            chara_w, chara_h = self.chara_image.get_size()
            pos_num = str(self.chara_info[2]) if len(self.chara_info) > 2 else "1"
            if pos_num == "1":  # 右端
                scale = (self.height * 0.85) / chara_h
                new_w = int(chara_w * scale)
                new_h = int(chara_h * scale)
                x = self.width - new_w - 40
                y = self.height - new_h
            elif pos_num == "2":  # 中央
                scale = (self.height * 1.00) / chara_h
                new_w = int(chara_w * scale)
                new_h = int(chara_h * scale)
                x = (self.width - new_w) // 2
                y = self.height - new_h
            elif pos_num == "3":  # 左端
                scale = (self.height * 0.90) / chara_h
                new_w = int(chara_w * scale)
                new_h = int(chara_h * scale)
                x = 40
                y = self.height - new_h
            else:
                scale = (self.height * 0.85) / chara_h
                new_w = int(chara_w * scale)
                new_h = int(chara_h * scale)
                x = self.width - new_w - 40
                y = self.height - new_h
            chara_img = pygame.transform.scale(self.chara_image, (new_w, new_h))
            screen.blit(chara_img, (x, y))

        # --- 半透明テキストウィンドウ ---
        text_surf = pygame.Surface((self.text_window_rect.width, self.text_window_rect.height), pygame.SRCALPHA)
        text_surf.fill((30, 30, 30, 180))  # RGBA: 180は透明度（0=完全透明, 255=不透明）
        pygame.draw.rect(text_surf, (200, 200, 200, 220), text_surf.get_rect(), 3, border_radius=15)
        screen.blit(text_surf, (self.text_window_rect.x, self.text_window_rect.y))

        # テキスト描画部分
        line_height = self.font.get_height() + 10
        start = max(0, len(self.history) - self.max_history)
        y = self.text_window_rect.y + 30
        for i, entry in enumerate(self.history[start:]):
            name = entry["name"]
            text = entry["text"]
            # ノベルゲー風：一番下の行だけタイプライター演出
            if i == len(self.history[start:]) - 1 and self.is_text_animating:
                display_text = text[:self.text_display_index]
            else:
                display_text = text
            # 名前がある場合は色付きで表示
            if name:
                name_color = self.name_color_map.get(name, (255,255,255))
                name_surface = self.font.render(name, True, name_color)
                screen.blit(name_surface, (self.text_window_rect.x + 30, y))
                name_w = name_surface.get_width()
                # テキストは白で名前の右隣に表示
                text_surface = self.font.render(display_text, True, (255,255,255))
                screen.blit(text_surface, (self.text_window_rect.x + 30 + name_w + 10, y))
            else:
                text_surface = self.font.render(display_text, True, (255,255,255))
                screen.blit(text_surface, (self.text_window_rect.x + 30, y))
            y += line_height

        # 選択肢ボタン
        self.choice_buttons = []
        if self.show_choices and self.choices:
            btn_w, btn_h = 350, 60
            gap = 25
            num = len(self.choices)
            total_height = num * btn_h + (num - 1) * gap
            start_y = (self.height - total_height) // 2
            for idx, choice in enumerate(self.choices):
                label = choice.get("label", f"選択肢{idx+1}")
                x = (self.width - btn_w) // 2
                y = start_y + idx * (btn_h + gap)
                btn_rect = pygame.Rect(x, y, btn_w, btn_h)

                # 角丸の半透明ボタン本体
                btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
                # 角丸で塗りつぶし
                pygame.draw.rect(btn_surf, (20, 20, 20, 180), btn_surf.get_rect(), border_radius=18)
                # 角丸で白枠
                pygame.draw.rect(btn_surf, (255, 255, 255, 180), btn_surf.get_rect(), 2, border_radius=18)
                screen.blit(btn_surf, (x, y))

                # テキストはやや大きめ＆中央
                text_surface = self.font.render(label, True, (255, 255, 255))
                text_x = x + (btn_w - text_surface.get_width()) // 2
                text_y = y + (btn_h - text_surface.get_height()) // 2
                screen.blit(text_surface, (text_x, text_y))
                self.choice_buttons.append(btn_rect)
        # 戻るボタン
        #pygame.draw.rect(screen, (200, 50, 50), self.back_btn)
        #back_text = self.font.render("Back", True, (255, 255, 255))
        #screen.blit(back_text, (self.back_btn.x + 25, self.back_btn.y + 10))
        
        # 戻るボタン（draw_buttonで描画）
        self.back_btn = draw_button(screen, "Back", (self.back_btn.x, self.back_btn.y), 48, (200, 50, 50), (255, 255, 255))

        pygame.display.flip()

    def _wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines