import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface Game {
  id: number;
  name: string;
  description: string;
  coverImage: string;
  // TODO: Add more game fields
}

export const useGameStore = defineStore('game', () => {
  const games = ref<Game[]>([]);
  const selectedGame = ref<Game | null>(null);

  function setGames(newGames: Game[]) {
    games.value = newGames;
  }

  function selectGame(game: Game) {
    selectedGame.value = game;
  }

  return {
    games,
    selectedGame,
    setGames,
    selectGame,
  };
});
