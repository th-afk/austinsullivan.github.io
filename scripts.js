window.onload = () => {
	const text = ["Insert inspirational quotes here"];
	const x = Math.floor(Math.random() * text.length);
	$('#randomQuote').html(text[x]);
};

