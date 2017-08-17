window.onload = () => {
	const text = ["Awesome quote here",
	              'Such great quotes here'];
	const x = Math.floor(Math.random() * text.length);
	$('#randonQuote').html(text[x]);
};


