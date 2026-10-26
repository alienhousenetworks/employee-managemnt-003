import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient({http.Client? client, FlutterSecureStorage? storage}) : _client = client ?? http.Client(), _storage = storage ?? const FlutterSecureStorage();
  final http.Client _client;
  final FlutterSecureStorage _storage;
  static const baseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000/api/v1');
  Future<void> signIn(String username, String password) async {
    final response = await _client.post(Uri.parse('$baseUrl/auth/token/'), headers: {'Content-Type':'application/json'}, body: jsonEncode({'username':username,'password':password}));
    if (response.statusCode != 200) throw Exception('Sign-in failed. Check credentials and API connectivity.');
    final body = jsonDecode(response.body) as Map<String,dynamic>;
    final access = body['access'] as String?; final refresh = body['refresh'] as String?;
    if (access == null || refresh == null) throw Exception('The authentication response was incomplete.');
    await _storage.write(key:'access_token', value:access); await _storage.write(key:'refresh_token', value:refresh);
  }
  Future<Map<String,dynamic>> currentUser() async {
    final token = await _storage.read(key:'access_token'); if (token == null) throw Exception('You are signed out.');
    final response = await _client.get(Uri.parse('$baseUrl/me/'), headers:{'Authorization':'Bearer $token','Accept':'application/json'});
    if (response.statusCode == 401) { await signOut(); throw Exception('Your session expired. Please sign in again.'); }
    if (response.statusCode != 200) throw Exception('Unable to load your profile (' + response.statusCode.toString() + ').');
    return jsonDecode(response.body) as Map<String,dynamic>;
  }
  Future<List<dynamic>> feed(String organizationId) async {
    final token = await _storage.read(key:'access_token'); if (token == null) throw Exception('You are signed out.');
    final response = await _client.get(Uri.parse('$baseUrl/feed/posts/'), headers:{'Authorization':'Bearer $token','X-Organization-ID':organizationId,'Accept':'application/json'});
    if (response.statusCode != 200) throw Exception('Unable to load the feed (' + response.statusCode.toString() + ').');
    final body = jsonDecode(response.body); return body is List ? body : (body['results'] as List? ?? <dynamic>[]);
  }
  Future<void> signOut() async { await _storage.delete(key:'access_token'); await _storage.delete(key:'refresh_token'); }
}
