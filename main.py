import pygame
import sys
import os  # パス確認用

def run_game(start_scene):
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    pygame.display.set_caption("My Game")
    clock = pygame.time.Clock()
    
    # デバッグ情報：Pythonパスとカレントディレクトリを確認
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Available modules in scenes directory:")
    try:
        scenes_dir = os.path.join(os.getcwd(), "scenes")
        if os.path.exists(scenes_dir):
            files = os.listdir(scenes_dir)
            for file in files:
                print(f"  - {file}")
    except Exception as e:
        print(f"Error listing scenes directory: {e}")

    current_scene = start_scene

    while True:
        # イベント取得
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        
        # 基本的なイベント処理
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        try:
            # シーン処理
            current_scene.process_input(events, keys)
            current_scene.update()
            current_scene.render(screen)
            
            # シーン変更があれば次のシーンへ
            if current_scene.next_scene != current_scene:
                print(f"Switching scene to: {current_scene.next_scene.__class__.__name__}")
                current_scene = current_scene.next_scene
                pygame.event.clear()  # シーン切替時にイベントをクリア
        except Exception as e:
            print(f"Error in game loop: {e}")
            # クリティカルなエラーの場合は終了
            if "GameScene" in str(e) and "not defined" in str(e):
                print("Critical error: GameScene not found. Check imports.")
                # scenes ディレクトリにゲームシーンファイルがあるか確認
                try:
                    if os.path.exists(os.path.join("scenes", "game.py")):
                        print("game.py exists but could not be imported.")
                    else:
                        print("game.py does not exist in scenes directory.")
                except:
                    pass
            
        # フレームレート制御
        clock.tick(60)

if __name__ == "__main__":
    from scenes.title import HomeScene  # home_sceneに修正
    run_game(HomeScene())