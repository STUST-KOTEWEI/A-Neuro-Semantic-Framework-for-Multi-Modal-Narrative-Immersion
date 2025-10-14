
import 'dart:convert';
import 'package:http/http.dart' as http;

// A simple model class to represent a book from the Gutendex API.
class Book {
  final int id;
  final String title;
  final List<String> authors;
  final String textUrl;

  Book({
    required this.id,
    required this.title,
    required this.authors,
    required this.textUrl,
  });

  // Factory constructor to create a Book from a JSON object.
  factory Book.fromJson(Map<String, dynamic> json) {
    // Find the plain text URL.
    final formats = json['formats'] as Map<String, dynamic>;
    String textUrl = formats['text/plain; charset=us-ascii'] ?? 
                     formats['text/plain; charset=utf-8'] ?? 
                     formats['text/plain'] ??
                     '';

    return Book(
      id: json['id'],
      title: json['title'],
      authors: (json['authors'] as List)
          .map((author) => author['name'] as String)
          .toList(),
      textUrl: textUrl,
    );
  }
}

// Service class to interact with the Gutendex API.
class GutenbergService {
  final String _baseUrl = 'https://gutendex.com/books';

  // Searches for books based on a query.
  Future<List<Book>> searchBooks(String query) async {
    final response = await http.get(Uri.parse('$_baseUrl?search=${Uri.encodeComponent(query)}'));

    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      final results = data['results'] as List;
      
      // Filter out books that don't have a plain text version.
      final books = results
          .map((json) => Book.fromJson(json))
          .where((book) => book.textUrl.isNotEmpty)
          .toList();
          
      return books;
    } else {
      throw Exception('Failed to load books');
    }
  }

  // Fetches the plain text content of a book from a given URL.
  Future<String> fetchBookText(String url) async {
    final response = await http.get(Uri.parse(url));

    if (response.statusCode == 200) {
      // The response body is already a string, but we decode using utf8
      // to handle special characters correctly.
      return utf8.decode(response.bodyBytes);
    } else {
      throw Exception('Failed to load book text');
    }
  }
}
