import 'package:flutter/material.dart';
import '../services/api_client.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget { const LoginScreen({super.key}); @override State<LoginScreen> createState() => _LoginScreenState(); }
class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>(); final _username = TextEditingController(); final _password = TextEditingController(); final _api = ApiClient();
  bool _loading = false; String? _error;
  @override void dispose() { _username.dispose(); _password.dispose(); super.dispose(); }
  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() { _loading = true; _error = null; });
    try {
      await _api.signIn(_username.text.trim(), _password.text); final me = await _api.currentUser();
      if (!mounted) return; final organizations = (me['organizations'] as List<dynamic>? ?? []);
      if (organizations.isEmpty) { setState(() => _error = 'This account has no active agency membership. Ask an administrator.'); await _api.signOut(); return; }
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => HomeScreen(api: _api, organization: organizations.first as Map<String,dynamic>)));
    } catch (e) { if (mounted) setState(() => _error = e.toString().replaceFirst('Exception: ','')); }
    finally { if (mounted) setState(() => _loading = false); }
  }
  @override Widget build(BuildContext context) => Scaffold(body: SafeArea(child: Center(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: ConstrainedBox(constraints: const BoxConstraints(maxWidth:440), child: Form(key:_formKey, child: Column(crossAxisAlignment:CrossAxisAlignment.stretch, children:[
    const Icon(Icons.hub_outlined, size:54), const SizedBox(height:18), const Text('ALIENHOUSE OS', textAlign:TextAlign.center, style:TextStyle(fontSize:22,fontWeight:FontWeight.w800)), const SizedBox(height:8), const Text('Sign in to your agency workspace', textAlign:TextAlign.center), const SizedBox(height:28),
    TextFormField(controller:_username, autofillHints:const [AutofillHints.username], decoration:const InputDecoration(labelText:'Username', border:OutlineInputBorder()), validator:(v)=>v==null||v.trim().isEmpty?'Enter your username':null), const SizedBox(height:14),
    TextFormField(controller:_password, obscureText:true, autofillHints:const [AutofillHints.password], decoration:const InputDecoration(labelText:'Password', border:OutlineInputBorder()), validator:(v)=>v==null||v.isEmpty?'Enter your password':null),
    if (_error != null) ...[const SizedBox(height:12), Text(_error!, style:TextStyle(color:Theme.of(context).colorScheme.error))], const SizedBox(height:20), FilledButton(onPressed:_loading?null:_submit, child:Text(_loading?'Signing in…':'Sign in')), const SizedBox(height:12), Text('API: ' + ApiClient.baseUrl, textAlign:TextAlign.center, style:Theme.of(context).textTheme.bodySmall),
  ]))))));
}
