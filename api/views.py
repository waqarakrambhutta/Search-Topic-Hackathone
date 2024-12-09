# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer  # To disable template rendering
from .utils import fetch_news_articles, scrape_article, generate_summary_with_groq, gen_textpost, gen_Imagepost, askoptions

class ArticleSummaryAPIView(APIView):
    # Only allow POST requests
    renderer_classes = [JSONRenderer]  # Render as JSON and avoid rendering templates
    
    def post(self, request, *args, **kwargs):
        # Extract values from the POST data
        topic = request.data.get('topic')
        platform = request.data.get('platform')
        image = request.data.get('image')  # Should be 1 or 0
        video = request.data.get('video')  # Should be 1 or 0 (though not used in the script)
        meme = request.data.get('meme')    # Should be 1 or 0 (though not used in the script)

        if not topic or not platform:
            return Response({"error": "Both topic and platform must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Call the backend function to fetch, scrape, summarize, and generate the output
        try:
            # Fetch articles based on the topic
            articles = fetch_news_articles(topic)
            if not articles:
                return Response({"error": "No articles found for the given topic."}, status=status.HTTP_404_NOT_FOUND)

            articles_data = []

            for i, (title, url) in enumerate(articles, start=1):
                # Scrape article content
                article_text = scrape_article(url)
                if article_text:
                    # Generate the summary
                    summary = generate_summary_with_groq(article_text)
                else:
                    summary = "Failed to generate summary due to missing content."

                articles_data.append({
                    "title": title,
                    "url": url,
                    "summary": summary
                })

            post_content = gen_textpost(articles_data, platform, topic)

            if image == 1:
                gen_Imagepost(post_content, platform, topic)

            # Prepare the response with the article data and the generated post content
            return Response({
                "articles": articles_data,
                "post_content": post_content,
                "message": "Content generated successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
