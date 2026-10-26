import 'package:flutter_test/flutter_test.dart';
import 'package:agency_workforce_mobile/main.dart';

void main() {
  testWidgets('shows the agency workspace and explicit offline state', (tester) async {
    await tester.pumpWidget(const AgencyWorkforceApp());
    expect(find.text('Your agency workspace'), findsOneWidget);
    expect(find.textContaining('Offline preview'), findsOneWidget);
    expect(find.text('My work'), findsOneWidget);
  });
}
