import { createApp } from 'https://unpkg.com/petite-vue?module'
createApp({
	count : 1,
	get plusOne() {
		return this.count + 1;
	},
	increment() {
		this.count++;
	}
}).mount()