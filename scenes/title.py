import pygame
from base import SceneBase
from utils.button import draw_button, is_button_clicked
from systems.volumes import VolumeManager




# 音楽初期化
pygame.mixer.init()
pygame.mixer.music.load("assets/MusicBox_08.mp3")
pygame.mixer.music.set_volume(0)
pygame.mixer.music.play(-1)




class HomeScene(SceneBase):
    def __init__(self):
        super().__init__()
        # 初期化処理
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.width, self.height = self.screen.get_size()
        
        # フラグとデバッグ用変数
        self.fade_completed = False
        self.debug_info = ""  # デバッグ情報

        # リソース読み込み
        self.bg = pygame.image.load("assets/BG/Home.png")
        self.bg = pygame.transform.scale(self.bg, (self.width, self.height))
        self.home_girl = pygame.image.load("assets/Cha/character1/1.png")
        self.title_font = pygame.font.Font("assets/LightNovel.otf", 150)
        self.debug_font = pygame.font.Font(None, 30)  # デバッグ用フォント
        self.title_text = self.title_font.render("魔王戦まで3日", True, (255, 255, 255),)

        # キャラリサイズ
        scale = 0.8
        ow, oh = self.home_girl.get_size()
        self.home_girl = pygame.transform.scale(self.home_girl, (int(ow * scale), int(oh * scale)))

        

        self.volume_manager = VolumeManager()
        
        # ボタン初期化
        self.setup_buttons()
        
        # フェード処理用
        self.fade_alpha = 255  # フェード用アルファ値
        self.fade_speed = 10

    def setup_buttons(self):
        """ボタンの初期化"""
        button_width = 240
        self.vol_up_btn = pygame.Rect(20, 950, button_width, 60)
        self.vol_down_btn = pygame.Rect(20, 1000, button_width, 60)
        self.start_btn = pygame.Rect(self.width // 2 - 98, self.height // 2, 196, 60)
        self.exit_btn = pygame.Rect(self.width // 2 - 90, self.height // 2 + 100, 180, 60)

    def draw_scene(self):
        """シーンの描画処理"""
        # 画面クリア
        self.screen.fill((0, 0, 0))
        
        # 背景と要素の描画
        self.screen.blit(self.bg, (0, 0))
        #self.screen.blit(self.home_girl, (1200, 210))
        self.screen.blit(self.title_text, (self.width // 2 - self.title_text.get_width() // 2, 200))
        

        # ボタン描画（色を少し暗めに調整）
        self.vol_up_btn = draw_button(self.screen, "Volume Up", (20, 910), 50, (50, 90, 130), (255, 255, 255))
        self.vol_down_btn = draw_button(self.screen, "Volume Down", (20, 990), 50, (50, 90, 130), (255, 255, 255))
        self.start_btn = draw_button(self.screen, "GameStart", (self.width // 2 - 98, self.height // 2), 50, (24, 100, 24), (255, 255, 255))
        self.exit_btn = draw_button(self.screen, "GameExit", (self.width // 2 - 90, self.height // 2 + 100), 50, (120, 24, 24), (255, 255, 255))
        
        # デバッグ情報表示
        if self.debug_info:
            debug_surface = self.debug_font.render(self.debug_info, True, (255, 0, 0))
            self.screen.blit(debug_surface, (10, 10))

    def process_input(self, events, keys):
        """入力処理"""
        # フェード中は入力を無視
        if not self.fade_completed:
            return
            
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # マウス位置を取得
                mouse_pos = pygame.mouse.get_pos()
                self.debug_info = f"Click: {mouse_pos}"
                
                if is_button_clicked(self.vol_up_btn, event):
                    self.volume_manager.increase_volume()
                    self.debug_info += " | Volume Up"
                elif is_button_clicked(self.vol_down_btn, event):
                    self.volume_manager.decrease_volume()
                    self.debug_info += " | Volume Down"
                elif is_button_clicked(self.exit_btn, event):
                    self.debug_info += " | Exit"
                    pygame.quit()
                    exit()
                elif is_button_clicked(self.start_btn, event):
                    self.debug_info += " | Game Start"
                    # 明示的にゲームシーンをインポート
                    try:
                        from scenes.game import GameScene
                        # シーン切り替え前にデバッグ表示を一度更新
                        self.render(self.screen)
                        pygame.display.flip()
                        pygame.time.delay(500)  # デバッグ情報を確認するための遅延
                        self.switch_to_scene(GameScene())
                    except Exception as e:
                        self.debug_info = f"Error: {str(e)}"

    def render(self, screen):
        """描画処理"""
        # 通常の描画
        self.draw_scene()
        
        # フェードエフェクト処理（まだフェードが完了していない場合）
        if not self.fade_completed:
            # フェード用の黒いオーバーレイ
            fade_surface = pygame.Surface((self.width, self.height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            screen.blit(fade_surface, (0, 0))
            
            # フェードアルファ値を更新
            self.fade_alpha -= self.fade_speed
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_completed = True
                # フェード完了時にイベントキューをクリア
                pygame.event.clear()
        
        # 画面を更新
        pygame.display.flip()

    def update(self):
        """更新処理"""
        self.clock.tick(60)  # フレームレート制御