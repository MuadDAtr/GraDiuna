import pygame
from random import randint

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 720
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.font.init()
font = pygame.font.SysFont("Arial", 30)

# Kolory – łatwo modyfikowalne
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Player:
    def __init__(self, name):
        self.name = name
        self.x_cord = 0  
        self.y_cord = 360  
        self.image = pygame.image.load("gracz.png")
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 6
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
    
    def tick(self, keys):
        if keys[pygame.K_w]:
            self.y_cord -= self.speed
        if keys[pygame.K_a]:
            self.x_cord -= self.speed
        if keys[pygame.K_d]:
            self.x_cord += self.speed
        if keys[pygame.K_s]:
            self.y_cord += self.speed

        # Teleportacja – gdy wychodzimy poza okno, pojawiamy się po przeciwnej stronie
        if self.x_cord < 0:
            self.x_cord = WINDOW_WIDTH - self.width
        elif self.x_cord > WINDOW_WIDTH - self.width:
            self.x_cord = 0

        if self.y_cord < 0:
            self.y_cord = WINDOW_HEIGHT - self.height
        elif self.y_cord > WINDOW_HEIGHT - self.height:
            self.y_cord = 0

        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
    
    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))

class Treasure:
    def __init__(self):
        self.x_cord = randint(0, WINDOW_WIDTH)
        self.y_cord = randint(0, WINDOW_HEIGHT)
        self.image = pygame.image.load("skarb.png")
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
    
    def tick(self):
        self.hitbox = pygame.Rect(self.x_cord, self.y_cord, self.width, self.height)
    
    def draw(self):
        window.blit(self.image, (self.x_cord, self.y_cord))

def zapisz_wynik(name, score):
    with open("ranking.txt", "a") as f:
        f.write(f"{name}: {score}\n")

def wyswietl_ranking():
    try:
        with open("ranking.txt", "r") as f:
            ranking = f.readlines()
    except FileNotFoundError:
        ranking = []
    return ranking[-5:]  # wyświetlamy ostatnie 5 wyników

def main():
    clock = pygame.time.Clock()
    running = True

    # Stany gry: "input" - wpisywanie imienia, "play" - rozgrywka, "end" - ekran końcowy
    game_state = "input"
    name_input = ""
    player = None
    score = 0
    treasures = []
    spawn_timer = 0
    game_duration = 120  # czas gry w sekundach
    start_time = None

    # Ładowanie tła – w fazie gry używamy obrazu, ekran input oraz end będą miały czarne tło
    background = pygame.image.load("gratlo.png")

    while running:
        dt = clock.tick(60) / 1000  # delta time (czas między klatkami) w sekundach

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "input":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if name_input != "":
                            player = Player(name_input)
                            game_state = "play"
                            start_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode

        # W zależności od stanu, rysujemy odpowiedni ekran
        if game_state == "input":
            window.fill(BLACK)
            instruction_text = font.render("Wpisz swoje imie: " + name_input, True, WHITE)
            window.blit(instruction_text, (50, WINDOW_HEIGHT // 2))
        
        elif game_state == "play":
            # Obliczamy pozostały czas
            elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
            remaining_time = max(0, int(game_duration - elapsed_time))

            # Jeśli czas minął, przechodzimy do stanu 'end' i zapisujemy wynik.
            if elapsed_time >= game_duration:
                game_state = "end"
                zapisz_wynik(player.name, score)

            # Aktualizacja rozgrywki
            keys = pygame.key.get_pressed()
            player.tick(keys)
            spawn_timer += dt
            if spawn_timer >= 3:
                spawn_timer = 0
                treasures.append(Treasure())
            
            # Sprawdzamy kolizje gracza z skarbami
            for treasure in treasures[:]:
                treasure.tick()
                if player.hitbox.colliderect(treasure.hitbox):
                    treasures.remove(treasure)
                    score += 1

            # Rysowanie tła, gracza, skarbów oraz wyświetlanie wyniku, imienia i zegara
            window.blit(background, (0, 0))
            player.draw()
            for treasure in treasures:
                treasure.draw()

            score_text = font.render(f"Score: {score}", True, WHITE)
            timer_text = font.render(f"Czas: {remaining_time}", True, WHITE)
            name_text = font.render(f"Gracz: {player.name}", True, WHITE)

            window.blit(score_text, (50, 20))
            window.blit(timer_text, (500, 20))
            window.blit(name_text, (50, 60))
        
        elif game_state == "end":
            # Ekran końcowy z wynikiem oraz rankingiem
            window.fill(BLACK)
            end_text = font.render("Koniec gry!", True, WHITE)
            final_score_text = font.render(f"Twoj wynik: {score}", True, WHITE)
            window.blit(end_text, (WINDOW_WIDTH // 2 - end_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
            window.blit(final_score_text, (WINDOW_WIDTH // 2 - final_score_text.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
            
            ranking = wyswietl_ranking()
            ranking_title = font.render("Ranking (ostatnie 5 wynikow):", True, WHITE)
            window.blit(ranking_title, (50, 100))
            for i, entry in enumerate(reversed(ranking)):
                entry_text = font.render(entry.strip(), True, WHITE)
                window.blit(entry_text, (50, 140 + i * 30))
        
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
