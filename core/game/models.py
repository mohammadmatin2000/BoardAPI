from django.db import models

# ======================================================================================================================
class Game(models.Model):
    player_name = models.CharField(max_length=100, default="Player")

    board_state = models.JSONField(default=list)  # وضعیت مهره‌ها (24 خانه)
    current_turn = models.CharField(max_length=10, default="player")
    is_finished = models.BooleanField(default=False)

    # فیلدهای اضافی برای GameState
    first_hit = models.IntegerField(default=0)
    first_borne = models.IntegerField(default=0)
    second_hit = models.IntegerField(default=0)
    second_borne = models.IntegerField(default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.id} - Turn: {self.current_turn}"

# ======================================================================================================================
class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    player = models.CharField(max_length=10)
    move_data = models.JSONField()  # حرکت مهره‌ها
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.player} move in Game {self.game.id}"
# ======================================================================================================================