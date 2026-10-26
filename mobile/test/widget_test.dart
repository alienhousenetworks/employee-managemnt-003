import 'package:flutter_test/flutter_test.dart';
import 'package:agency_workforce_mobile/main.dart';
void main() { testWidgets('shows the sign-in form', (tester) async { await tester.pumpWidget(const AgencyWorkforceApp()); expect(find.text('Sign in to your agency workspace'), findsOneWidget); expect(find.text('Username'), findsOneWidget); expect(find.text('Password'), findsOneWidget); }); }
