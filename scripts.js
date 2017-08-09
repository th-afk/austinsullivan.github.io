window.onload = () => {
	const text = ["Insert inspirational quotes here", "So inspirational", "That's terrific"];
	const x = Math.floor(Math.random() * text.length);
	$('#randomQuote').html(text[x]);
};


